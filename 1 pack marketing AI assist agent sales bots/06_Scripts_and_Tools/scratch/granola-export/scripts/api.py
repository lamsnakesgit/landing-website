"""
granola-export — reusable Python library for the Granola REST API.

Reads tokens from the locally-installed Granola Mac app session.
Handles auth, paginated fetches, gzip decompression, and ProseMirror→Markdown.

Usage as a library:

    from api import load_workos_token, api_post, list_all_documents, get_transcript, pm_to_md

    token = load_workos_token()
    docs = list_all_documents(token)
    for doc in docs:
        transcript = get_transcript(doc["id"], token)
        ...

Most callers should use scripts/extract.py instead — this module is the engine.
"""

from __future__ import annotations

import gzip
import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from base64 import urlsafe_b64decode
from pathlib import Path
from typing import Any

# ─── Constants ────────────────────────────────────────────────────────────────

GRANOLA_SUPPORT_DIR = Path.home() / "Library/Application Support/Granola"
SUPABASE_FILE = GRANOLA_SUPPORT_DIR / "supabase.json"
LOCAL_STATE_FILE = GRANOLA_SUPPORT_DIR / "local-state.json"

API_BASE = "https://api.granola.ai"
STREAM_API_BASE = "https://stream.api.granola.ai"
USER_AGENT = "Granola/7.155.1 (macOS)"

# Sub-services discovered during teardown — keyed by name
SUBSERVICES = {
    "berry": "https://berry.api.granola.ai",
    "chia": "https://chia.api.granola.ai",
    "cinnamon": "https://cinnamon.api.granola.ai",
    "maple": "https://maple.api.granola.ai",
    "pecan": "https://pecan.api.granola.ai",
}


# ─── Auth ─────────────────────────────────────────────────────────────────────

class TokenError(Exception):
    """Raised when token loading or refresh fails."""


def _read_supabase_json() -> dict:
    """
    Read the Granola Mac app's supabase.json. Note: top-level values are
    JSON-stringified inner JSON (a JSON.stringify was applied before storage).
    Both layers must be parsed.
    """
    if not SUPABASE_FILE.exists():
        raise TokenError(
            f"Granola auth file not found at {SUPABASE_FILE}. "
            "Is the Granola Mac app installed and logged in?"
        )
    outer = json.loads(SUPABASE_FILE.read_text())
    parsed = {}
    for key, val in outer.items():
        if isinstance(val, str) and val.startswith("{"):
            try:
                parsed[key] = json.loads(val)
            except json.JSONDecodeError:
                parsed[key] = val
        else:
            parsed[key] = val
    return parsed


def _decode_jwt_claims(token: str) -> dict:
    """Decode a JWT's claims segment (no signature verification)."""
    try:
        payload_b64 = token.split(".")[1]
        # Pad base64 if needed
        padding = "=" * (4 - len(payload_b64) % 4)
        return json.loads(urlsafe_b64decode(payload_b64 + padding))
    except Exception:
        return {}


def load_workos_token() -> str:
    """
    Return the active WorkOS access token. Raises TokenError if missing or
    expired. Does not auto-refresh — call `refresh_workos_token()` separately
    when needed (or run `scripts/refresh_token.sh`).
    """
    data = _read_supabase_json()
    workos = data.get("workos_tokens")
    if not isinstance(workos, dict) or "access_token" not in workos:
        raise TokenError("No WorkOS access_token in supabase.json")

    token = workos["access_token"]
    claims = _decode_jwt_claims(token)
    exp = claims.get("exp", 0)
    now = int(time.time())
    if exp and exp <= now:
        raise TokenError(
            f"WorkOS access token expired {now - exp}s ago. "
            "Run scripts/refresh_token.sh to mint a fresh one, or open the Granola app to re-auth."
        )
    return token


def load_user_info() -> dict:
    """Return the cached user_info object (email, id, workspace_ids, etc.)."""
    return _read_supabase_json().get("user_info") or {}


def refresh_workos_token() -> str:
    """
    Mint a fresh WorkOS access token using the refresh_token from supabase.json.
    The WorkOS endpoint pattern is the OAuth2 standard; client_id comes from
    the existing token's claims.

    Returns the new access_token. Does NOT update supabase.json (the Granola
    app would be confused). Use the returned token in-process.
    """
    data = _read_supabase_json()
    workos = data.get("workos_tokens") or {}
    refresh = workos.get("refresh_token")
    if not refresh:
        raise TokenError("No refresh_token in workos_tokens")

    # client_id comes from the existing access token's claims
    old = workos.get("access_token", "")
    claims = _decode_jwt_claims(old)
    client_id = claims.get("client_id")
    iss = claims.get("iss", "")
    # Issuer looks like https://auth.granola.ai/user_management/<client_id>
    # Token endpoint is the canonical WorkOS shape.
    if not client_id or not iss:
        raise TokenError("Could not derive WorkOS client_id from existing token claims")

    # WorkOS OAuth token endpoint (path may vary; this matches standard OIDC)
    token_url = f"https://auth.granola.ai/oauth2/token"
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
    }).encode()

    req = urllib.request.Request(
        token_url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()
        except Exception:
            err_body = ""
        raise TokenError(f"WorkOS refresh failed: HTTP {e.code} {err_body[:300]}")

    new_token = payload.get("access_token")
    if not new_token:
        raise TokenError(f"WorkOS refresh response missing access_token: {payload}")
    return new_token


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

class ApiError(Exception):
    """Raised on non-2xx responses or transport failure."""


def api_post(
    endpoint: str,
    body: dict | None = None,
    token: str | None = None,
    timeout: int = 25,
    base: str = API_BASE,
) -> Any:
    """
    POST to a Granola endpoint with the standard headers. Auto-decompresses
    gzipped responses. Returns parsed JSON, or raw text if not JSON.

    `endpoint` is appended to `base` (or pass a full URL as `base` and an
    empty endpoint if you want full control). Always sends gzip Accept-Encoding.
    """
    if token is None:
        token = load_workos_token()
    if body is None:
        body = {}
    url = base + endpoint if endpoint.startswith("/") else f"{base}/{endpoint}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            text = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            err_raw = e.read()
            if e.headers.get("Content-Encoding") == "gzip":
                err_raw = gzip.decompress(err_raw)
            err_text = err_raw.decode("utf-8", errors="replace")
        except Exception:
            err_text = ""
        raise ApiError(f"HTTP {e.code} on POST {url}: {err_text[:500]}")
    except urllib.error.URLError as e:
        raise ApiError(f"URLError on POST {url}: {e}")

    # Many Granola endpoints return JSON; a few (like /v1/hello) return plain text.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# ─── High-level convenience functions ─────────────────────────────────────────

def hello(token: str | None = None) -> str:
    """Auth probe. Returns 'hello <user-id>' on success."""
    return api_post("/v1/hello", body={}, token=token)


def get_user_info(token: str | None = None) -> dict:
    return api_post("/v1/get-user-info", body={}, token=token)


def list_documents_page(offset: int = 0, limit: int = 100, token: str | None = None) -> dict:
    """One page of /v2/get-documents. Returns {'docs': [...], 'deleted': [...]}."""
    return api_post("/v2/get-documents", body={"limit": limit, "offset": offset}, token=token)


def list_all_documents(token: str | None = None, page_size: int = 100,
                        sleep_between_pages: float = 0.2) -> list[dict]:
    """Paginate through /v2/get-documents and return the full doc list."""
    if token is None:
        token = load_workos_token()
    all_docs: list[dict] = []
    offset = 0
    while True:
        page = list_documents_page(offset=offset, limit=page_size, token=token)
        docs = page.get("docs") or []
        all_docs.extend(docs)
        if len(docs) < page_size:
            break
        offset += page_size
        time.sleep(sleep_between_pages)
    # De-dupe by id (defensive)
    seen = set()
    unique = []
    for d in all_docs:
        if d.get("id") not in seen:
            seen.add(d.get("id"))
            unique.append(d)
    return unique


def get_transcript(document_id: str, token: str | None = None) -> list[dict]:
    """Fetch the transcript array for a document. Returns [] if none."""
    out = api_post(
        "/v1/get-document-transcript",
        body={"document_id": document_id},
        token=token,
    )
    return out if isinstance(out, list) else []


def get_panels(document_id: str, token: str | None = None) -> list[dict]:
    """Fetch AI summary panels (ProseMirror JSON) for a document."""
    out = api_post(
        "/v1/get-document-panels",
        body={"document_id": document_id},
        token=token,
    )
    return out if isinstance(out, list) else []


def get_attachments(document_id: str, token: str | None = None) -> list[dict]:
    out = api_post(
        "/v1/get-attachments",
        body={"document_id": document_id},
        token=token,
    )
    return out if isinstance(out, list) else []


def get_recipes(token: str | None = None) -> dict:
    """
    All recipes available to the user. Returns a dict with categories:
    `userRecipes`, `sharedRecipes`, `publicRecipes`, `unlistedRecipes`,
    `defaultRecipes`, plus `recipesUsage` (per-recipe usage stats).
    Most users only have non-empty `publicRecipes` (the community library).
    """
    out = api_post("/v1/get-recipes", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_panel_templates(token: str | None = None) -> list[dict]:
    """Default + user-custom panel templates. Each has id, title, category, sections."""
    out = api_post("/v1/get-panel-templates", body={}, token=token)
    return out if isinstance(out, list) else []


def get_document_lists(token: str | None = None) -> dict:
    """
    Folders / lists. Returns {'lists': [...]}. **Uses v2** — `/v1/get-document-lists`
    returns "Not implemented" on the current backend.
    """
    out = api_post("/v2/get-document-lists", body={}, token=token)
    return out if isinstance(out, dict) else {"lists": []}


def get_shared_documents(token: str | None = None) -> dict:
    """Returns {'docs': [...]}."""
    out = api_post("/v1/get-shared-documents", body={}, token=token)
    return out if isinstance(out, dict) else {"docs": []}


def get_feature_flags(token: str | None = None) -> dict:
    out = api_post("/v1/get-feature-flags", body={}, token=token)
    return out if isinstance(out, dict) else {}


# ─── Auxiliary endpoints (folders, recipes, templates, people, etc.) ─────────
# These were probed and confirmed working on a real Granola account. Some are
# gated server-side per feature flag (action_items / pre_meeting_briefs /
# follow_up_emails return 403 "feature not enabled" on free trial accounts).
# The library raises ApiError on those; callers should catch and treat as
# "not available for this user".


def get_user_preferences(token: str | None = None) -> dict:
    out = api_post("/v1/get-user-preferences", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_workspaces(token: str | None = None) -> dict:
    out = api_post("/v1/get-workspaces", body={}, token=token)
    return out if isinstance(out, dict) else {"workspaces": []}


def get_subscriptions(token: str | None = None) -> dict:
    out = api_post("/v1/get-subscriptions", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_current_subscription(token: str | None = None) -> dict:
    out = api_post("/v1/get-current-subscription", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_selected_calendars(token: str | None = None) -> dict:
    out = api_post("/v1/get-selected-calendars", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_google_events(token: str | None = None) -> list[dict]:
    out = api_post("/v1/get-google-events", body={}, token=token)
    return out if isinstance(out, list) else []


def get_chat_models(token: str | None = None) -> dict:
    out = api_post("/v1/get-chat-models", body={}, token=token)
    return out if isinstance(out, dict) else {}


def get_integrations(token: str | None = None) -> list[dict]:
    """Returns connected integration records (Affinity API key, etc.)."""
    out = api_post("/v1/get-integrations", body={}, token=token)
    return out if isinstance(out, list) else []


def get_people(token: str | None = None) -> list[dict]:
    out = api_post("/v1/get-people", body={}, token=token, base=SUBSERVICES["pecan"])
    return out if isinstance(out, list) else []


def get_paywall_status(token: str | None = None) -> dict:
    out = api_post("/v1/get-paywall-status", body={}, token=token, base=SUBSERVICES["cinnamon"])
    return out if isinstance(out, dict) else {}


def list_available_integrations(token: str | None = None) -> dict:
    out = api_post("/v1/list-available-integrations", body={}, token=token, base=SUBSERVICES["chia"])
    return out if isinstance(out, dict) else {"integrations": []}


# ─── Paid-tier endpoints (defensive — return 403 "feature not enabled" on free) ──
# These return 403 on free trial accounts. Helpers exist so they auto-cover
# paid users without code changes; they raise ApiError on free accounts and
# the extract.py aux loop catches that gracefully.
#
# Response shapes here are best-effort guesses based on REST conventions and
# adjacent endpoints. If you're on a paid tier and shapes differ, please open
# an issue with the actual response (redact PII).

def get_action_items(token: str | None = None) -> list[dict]:
    """
    Extracted action items as first-class entities. Paywalled — confirmed 403
    "feature not enabled" on free trial. On free accounts, action items still
    appear inside AI summary panels; this endpoint exposes them as structured
    entities for paid users.
    """
    out = api_post("/v1/get-action-items", body={}, token=token, base=SUBSERVICES["maple"])
    return out if isinstance(out, list) else []


def get_follow_up_emails(token: str | None = None) -> list[dict]:
    """AI-drafted follow-up email content per meeting. Paywalled (403 on free)."""
    out = api_post("/v1/get-follow-up-emails", body={}, token=token, base=SUBSERVICES["berry"])
    return out if isinstance(out, list) else []


def get_ambient_context(token: str | None = None) -> dict:
    """
    User's ambient context profile (cross-app signals captured via the
    `ambient_context.node` native module — frontmost app, OCR'd screen content,
    etc.). Paywalled (403 on free).
    """
    out = api_post("/v1/get-ambient-context", body={}, token=token, base=SUBSERVICES["berry"])
    return out if isinstance(out, dict) else {}


def get_about_me_profile(person_id: str, token: str | None = None) -> dict:
    """
    Auto-generated profile for a person (from meeting attendees). Per-person —
    needs `person_id` from `pecan/v1/get-people`.

    Notably **not paywalled** on free tier (verified live). Returns an empty
    dict for unknown person IDs rather than 403/404. Useful for enriching
    attendee data into rendered exports.
    """
    out = api_post(
        "/v1/get-about-me-profile",
        body={"person_id": person_id},
        token=token,
        base=SUBSERVICES["berry"],
    )
    return out if isinstance(out, dict) else {}


# ─── ProseMirror → Markdown ───────────────────────────────────────────────────

def pm_to_md(node: Any, depth: int = 0) -> str:
    """
    Convert a ProseMirror JSON document (or fragment) to Markdown.

    Handles dict nodes, list-of-nodes, bare strings, and None defensively —
    Granola's API occasionally returns a bare string where a node is expected,
    so the walker has to tolerate that case rather than crash.

    Supported node types: doc, heading, paragraph, bulletList, orderedList,
    listItem, codeBlock, blockquote, hardBreak, text (with bold/italic/code/link
    marks).
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(pm_to_md(c, depth) for c in node)
    if not isinstance(node, dict):
        return str(node)

    t = node.get("type", "")
    content = node.get("content") or []
    text = node.get("text", "") or ""
    marks = node.get("marks") or []

    if t == "text":
        s = text
        for m in marks:
            if not isinstance(m, dict):
                continue
            mt = m.get("type")
            if mt == "bold":
                s = f"**{s}**"
            elif mt == "italic":
                s = f"*{s}*"
            elif mt == "code":
                s = f"`{s}`"
            elif mt == "link":
                href = (m.get("attrs") or {}).get("href", "")
                s = f"[{s}]({href})"
        return s

    if t == "heading":
        level = (node.get("attrs") or {}).get("level", 2)
        return f"\n{'#' * level} {pm_to_md(content, depth)}\n\n"

    if t == "paragraph":
        return pm_to_md(content, depth) + "\n\n"

    if t in ("bulletList", "orderedList"):
        return pm_to_md(content, depth) + "\n"

    if t == "listItem":
        inner = pm_to_md(content, depth + 1).rstrip()
        prefix = "  " * depth + "- "
        lines = inner.split("\n")
        out = prefix + (lines[0] if lines else "") + "\n"
        for l in lines[1:]:
            out += ("  " * (depth + 1) + l if l else "") + "\n"
        return out

    if t == "codeBlock":
        lang = (node.get("attrs") or {}).get("language", "") or ""
        return f"\n```{lang}\n{pm_to_md(content)}\n```\n\n"

    if t == "hardBreak":
        return "\n"

    if t == "blockquote":
        inner = pm_to_md(content, depth).rstrip()
        return "\n".join("> " + l for l in inner.split("\n")) + "\n\n"

    # Default: recurse into content (handles 'doc' root and unknown types)
    return pm_to_md(content, depth)


# ─── Quick CLI for sanity checks ──────────────────────────────────────────────

def _main_cli():
    """Run as a script for a quick auth check + summary."""
    try:
        token = load_workos_token()
    except TokenError as e:
        print(f"Token error: {e}", file=sys.stderr)
        sys.exit(2)

    user = load_user_info()
    print(f"Logged in as: {user.get('email', '?')} (id={user.get('id', '?')[:8]}...)")

    h = hello(token)
    print(f"Auth probe: {h}")

    page = list_documents_page(offset=0, limit=1, token=token)
    print(f"First-doc fetch OK. Total visible in first page: {len(page.get('docs', []))}")
    print()
    print("API library is healthy. Use scripts/extract.py for full export.")


if __name__ == "__main__":
    _main_cli()
