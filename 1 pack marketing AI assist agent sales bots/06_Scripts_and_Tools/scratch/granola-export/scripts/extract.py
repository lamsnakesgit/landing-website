#!/usr/bin/env python3
"""
granola-export — full personal data extraction.

Extracts all of your Granola.ai meetings, transcripts, and AI summaries via the
REST API using your locally-stored auth tokens (no login needed). Output is
both raw JSON (for re-rendering or programmatic use) and rendered Markdown
(one file per meeting, sortable by date, ready to grep / import elsewhere).

Idempotent: skip-if-exists logic means re-running tops up new docs without
re-fetching old ones.

Usage:
    python3 extract.py                    # full export (meetings + aux + attachments)
    python3 extract.py --dest ~/exports   # custom output dir
    python3 extract.py --index-only       # only fetch document metadata
    python3 extract.py --skip-render      # fetch but don't generate Markdown
    python3 extract.py --no-extended      # skip aux endpoints + attachments
    python3 extract.py --workers 8        # tune concurrency for transcript fetches
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Make api.py importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api import (
    ApiError,
    TokenError,
    USER_AGENT,
    get_chat_models,
    get_current_subscription,
    get_document_lists,
    get_google_events,
    get_integrations,
    get_panel_templates,
    get_panels,
    get_paywall_status,
    get_people,
    get_recipes,
    get_selected_calendars,
    get_shared_documents,
    get_subscriptions,
    get_transcript,
    get_user_preferences,
    get_workspaces,
    hello,
    list_all_documents,
    list_available_integrations,
    load_user_info,
    load_workos_token,
    pm_to_md,
)


DEFAULT_DEST = Path.home() / "reference/granola/extracted/my-data"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def slugify(s: str, maxlen: int = 80) -> str:
    """
    Convert a doc title to a filesystem-safe slug.

    Note: Granola's AI title-generator occasionally produces titles with
    embedded newlines/tabs (when the generation goes off the rails). We
    collapse ALL whitespace — not just spaces — to a single hyphen so
    filenames are predictable.
    """
    if not s:
        return "untitled"
    # Drop punctuation that's not word-char / whitespace / hyphen
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    # Collapse any whitespace (spaces, newlines, tabs) into a hyphen
    s = re.sub(r"\s+", "-", s)
    # Collapse runs of hyphens
    s = re.sub(r"-+", "-", s)
    return s[:maxlen] or "untitled"


def fmt_attendees(people) -> str:
    if not isinstance(people, dict):
        return ""
    lines = []
    for kind in ("organizer", "attendees", "manual_attendee_edits"):
        items = people.get(kind) or []
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            continue
        for p in items:
            if not isinstance(p, dict):
                continue
            email = p.get("email", "") or ""
            name = p.get("displayName") or p.get("name") or ""
            if email or name:
                lines.append(f"- {name} <{email}>" if name else f"- {email}")
    return "\n".join(sorted(set(lines)))


def fmt_transcript(items) -> str:
    if not isinstance(items, list) or not items:
        return "(no transcript)"
    out = []
    for seg in items:
        if not isinstance(seg, dict):
            continue
        ts = seg.get("start_timestamp") or ""
        try:
            t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            tstr = t.strftime("%H:%M:%S")
        except Exception:
            tstr = (ts[:8] if ts else "        ")
        src = seg.get("source") or "?"
        src_label = {"microphone": "MIC", "system": "SYS"}.get(src, src.upper())
        text = (seg.get("text") or "").strip()
        if text:
            out.append(f"`{tstr}` **[{src_label}]** {text}")
    return "\n".join(out)


# ─── Main steps ───────────────────────────────────────────────────────────────

def step_fetch_index(dest: Path, token: str) -> dict:
    """Fetch full document list (paginated) and persist to docs.json."""
    docs_path = dest / "docs.json"
    print("[1/3] Fetching document index...", flush=True)
    docs = list_all_documents(token=token)
    bundle = {
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total": len(docs),
        "docs": docs,
    }
    docs_path.write_text(json.dumps(bundle, indent=2, default=str))
    print(f"      → {len(docs)} documents in {docs_path.name}", flush=True)
    return bundle


def _fetch_one(args):
    """Worker: fetch transcript + panels for one doc, save raw JSON."""
    doc_id, dest, token = args
    t_path = dest / "transcripts" / f"{doc_id}.json"
    p_path = dest / "panels" / f"{doc_id}.json"
    fetched = {"transcript": False, "panels": False}

    if not t_path.exists() or t_path.stat().st_size == 0:
        try:
            data = get_transcript(doc_id, token=token)
            t_path.write_text(json.dumps(data))
            fetched["transcript"] = True
        except (ApiError, TokenError) as e:
            t_path.write_text(json.dumps({"error": str(e)}))

    if not p_path.exists() or p_path.stat().st_size == 0:
        try:
            data = get_panels(doc_id, token=token)
            p_path.write_text(json.dumps(data))
            fetched["panels"] = True
        except (ApiError, TokenError) as e:
            p_path.write_text(json.dumps({"error": str(e)}))

    return doc_id, fetched


def step_fetch_payloads(dest: Path, bundle: dict, token: str, workers: int = 4):
    """Fetch transcripts + panels for every doc, in parallel."""
    (dest / "transcripts").mkdir(exist_ok=True)
    (dest / "panels").mkdir(exist_ok=True)
    docs = bundle["docs"]

    # Filter to docs that don't already have BOTH files saved
    todo = []
    for d in docs:
        doc_id = d.get("id")
        if not doc_id:
            continue
        t_ok = (dest / "transcripts" / f"{doc_id}.json").exists()
        p_ok = (dest / "panels" / f"{doc_id}.json").exists()
        if not (t_ok and p_ok):
            todo.append(doc_id)

    print(f"[2/3] Fetching transcripts + panels for {len(todo)}/{len(docs)} docs "
          f"({len(docs) - len(todo)} already on disk)...", flush=True)

    if not todo:
        print("      → all docs already fetched, skipping", flush=True)
        return

    started = time.time()
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        args_iter = ((doc_id, dest, token) for doc_id in todo)
        for doc_id, fetched in ex.map(_fetch_one, args_iter):
            done += 1
            if done % 25 == 0 or done == len(todo):
                elapsed = time.time() - started
                rate = done / elapsed if elapsed else 0
                eta = (len(todo) - done) / rate if rate else 0
                print(f"      → {done}/{len(todo)}  rate={rate:.1f}/s  eta={eta:.0f}s",
                      flush=True)


def step_fetch_aux(dest: Path, token: str):
    """Fetch single-shot endpoints (folders, recipes, templates, people, etc.)."""
    aux = dest / "aux"
    aux.mkdir(exist_ok=True)
    print("[aux] Fetching auxiliary endpoints...", flush=True)

    # (label, callable returning JSON-serializable, paywalled?)
    fetchers = [
        ("recipes",              lambda: get_recipes(token)),
        ("panel_templates",      lambda: get_panel_templates(token)),
        ("folders",              lambda: get_document_lists(token)),
        ("shared_documents",     lambda: get_shared_documents(token)),
        ("integrations",         lambda: get_integrations(token)),
        ("available_integrations", lambda: list_available_integrations(token)),
        ("user_preferences",     lambda: get_user_preferences(token)),
        ("workspaces",           lambda: get_workspaces(token)),
        ("subscriptions",        lambda: get_subscriptions(token)),
        ("current_subscription", lambda: get_current_subscription(token)),
        ("selected_calendars",   lambda: get_selected_calendars(token)),
        ("google_events",        lambda: get_google_events(token)),
        ("chat_models",          lambda: get_chat_models(token)),
        ("people",               lambda: get_people(token)),
        ("paywall_status",       lambda: get_paywall_status(token)),
    ]

    for name, fn in fetchers:
        out_path = aux / f"{name}.json"
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"      ✓ {name} (cached)", flush=True)
            continue
        try:
            data = fn()
            out_path.write_text(json.dumps(data, indent=2, default=str))
            shape = (f"list[{len(data)}]" if isinstance(data, list)
                     else f"dict({len(data)} keys)" if isinstance(data, dict)
                     else type(data).__name__)
            print(f"      ✓ {name} → {shape}", flush=True)
        except (ApiError, TokenError) as e:
            msg = str(e)
            tag = "(paywalled)" if "feature" in msg.lower() else "(failed)"
            out_path.write_text(json.dumps({"error": msg}))
            print(f"      ! {name} {tag}: {msg[:80]}", flush=True)


def step_fetch_attachments(dest: Path, bundle: dict):
    """Download all inline attachments. URLs are S3-presigned with short TTL."""
    att_dir = dest / "attachments"
    att_dir.mkdir(exist_ok=True)
    print("[att] Downloading attachments...", flush=True)

    index = []
    for doc in bundle["docs"]:
        atts = doc.get("attachments")
        if not atts:
            continue
        for a in atts:
            if isinstance(a, dict):
                index.append({
                    "document_id": doc["id"],
                    "title": doc.get("title"),
                    **a,
                })
    if not index:
        print("      → no attachments to download", flush=True)
        return

    (att_dir / "_index.json").write_text(json.dumps(index, indent=2, default=str))

    ok, fail, cached = 0, 0, 0
    for i, a in enumerate(index):
        url = a.get("url")
        if not url:
            continue
        aid = a.get("id", f"att_{i}")
        # Detect extension from URL path
        path = urlparse(url).path
        ext = ""
        if "." in path.split("/")[-1]:
            ext = "." + path.split("/")[-1].split(".")[-1].split("?")[0]
        out_file = att_dir / f"{aid}{ext}"
        if out_file.exists() and out_file.stat().st_size > 0:
            cached += 1
            continue
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                out_file.write_bytes(resp.read())
                ok += 1
        except Exception as e:
            fail += 1
            print(f"      ! {aid}: {e}", flush=True)

    total_kb = sum(p.stat().st_size for p in att_dir.glob("*") if p.is_file()) // 1024
    print(f"      → {ok} new, {cached} cached, {fail} failed ({total_kb} KB total)", flush=True)


def step_render_markdown(dest: Path, bundle: dict):
    """Render every doc as a Markdown file + master index."""
    out = dest / "meetings"
    out.mkdir(exist_ok=True)

    print(f"[3/3] Rendering {len(bundle['docs'])} markdown files...", flush=True)
    written = 0
    errors = 0
    index = []

    for doc in bundle["docs"]:
        try:
            doc_id = doc["id"]
            created = doc.get("created_at") or ""
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                datestr = dt.strftime("%Y-%m-%d")
                timestr = dt.strftime("%H%M")
            except Exception:
                datestr = "0000-00-00"
                timestr = "0000"
            title = (doc.get("title") or "untitled").strip()
            slug = slugify(title)
            fname = f"{datestr}_{timestr}_{slug}_{doc_id[:8]}.md"
            outpath = out / fname

            transcript = []
            panels = []
            try:
                with open(dest / "transcripts" / f"{doc_id}.json") as f:
                    transcript = json.load(f)
            except Exception:
                pass
            try:
                with open(dest / "panels" / f"{doc_id}.json") as f:
                    panels = json.load(f)
            except Exception:
                pass
            if not isinstance(transcript, list):
                transcript = []
            if not isinstance(panels, list):
                panels = []

            md = [
                f"# {title}\n",
                f"- **Date:** {created}",
                f"- **ID:** `{doc_id}`",
                f"- **Type:** {doc.get('type') or 'note'}",
            ]
            if doc.get("valid_meeting"):
                md.append("- **Valid meeting:** yes")
            if doc.get("privacy_mode_enabled"):
                md.append("- **Privacy mode:** ON (recording was marked private)")
            if doc.get("audio_file_handle"):
                md.append(f"- **Audio file (server-side, not downloadable):** `{doc['audio_file_handle']}`")
            if doc.get("status"):
                md.append(f"- **Status:** {doc['status']}")
            if doc.get("creation_source"):
                md.append(f"- **Created via:** {doc['creation_source']}")
            gce = doc.get("google_calendar_event")
            if isinstance(gce, dict):
                summary = gce.get("summary", "?")
                start_obj = gce.get("start") if isinstance(gce.get("start"), dict) else None
                start = (start_obj or {}).get("dateTime", "?")
                md.append(f"- **Calendar:** {summary} ({start})")
            md.append(f"- **Public:** {doc.get('public', False)}")
            md.append("")

            att = fmt_attendees(doc.get("people"))
            if att:
                md.append("## Attendees\n")
                md.append(att)
                md.append("")

            # Inline attachments (image attachments embedded in notes)
            atts = doc.get("attachments") or []
            if atts:
                md.append("## Attachments\n")
                for a in atts:
                    if isinstance(a, dict):
                        aid = a.get("id", "?")
                        typ = a.get("type", "?")
                        w, h = a.get("width", "?"), a.get("height", "?")
                        md.append(f"- `{aid}` ({typ}, {w}×{h}) — see `attachments/{aid}.*`")
                md.append("")

            notes_md = (doc.get("notes_markdown") or "").strip()
            if notes_md:
                md.append("## My Notes\n")
                md.append(notes_md)
                md.append("")

            if panels:
                md.append("---\n\n## AI Summaries\n")
                for panel in panels:
                    if not isinstance(panel, dict):
                        continue
                    ptitle = panel.get("title") or "(untitled panel)"
                    tslug = panel.get("template_slug") or ""
                    suffix = f" (template: `{tslug}`)" if tslug else ""
                    md.append(f"### {ptitle}{suffix}\n")
                    pcontent = panel.get("content")
                    if pcontent:
                        md.append(pm_to_md(pcontent).strip())
                        md.append("")
                    # Original AI version (pre-user-edit) — can differ from current
                    original = panel.get("original_content")
                    if original and original != pcontent:
                        md.append("\n#### Original AI version (before edits)\n")
                        md.append(pm_to_md(original).strip())
                        md.append("")
                    # AI-suggested follow-up questions
                    sq = panel.get("suggested_questions")
                    if sq and isinstance(sq, list):
                        md.append("\n#### Suggested follow-up questions\n")
                        for q in sq:
                            if isinstance(q, str):
                                md.append(f"- {q}")
                            elif isinstance(q, dict):
                                md.append(f"- {q.get('text') or q.get('question') or str(q)}")
                        md.append("")
                    # User feedback (thumbs up/down on the summary)
                    if panel.get("user_feedback"):
                        md.append(f"\n_User feedback on this panel: {panel['user_feedback']}_\n")

            if transcript:
                md.append("---\n\n## Transcript\n")
                md.append(fmt_transcript(transcript))
                md.append("")

            outpath.write_text("\n".join(md))
            written += 1
            index.append({
                "date": datestr,
                "time": timestr,
                "title": title,
                "id": doc_id,
                "fname": fname,
                "has_transcript": bool(transcript),
                "has_panels": bool(panels),
                "valid_meeting": doc.get("valid_meeting", False),
            })
        except Exception as e:
            errors += 1
            print(f"      ! err {doc.get('id', '?')}: {e}", file=sys.stderr)

    # Master index
    index.sort(key=lambda x: (x["date"], x["time"]))
    idx = [
        "# Granola Export — Meeting Index\n",
        f"Total: **{len(index)}** documents extracted on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Legend: `[M]` valid meeting · `[T]` transcript · `[S]` AI summaries\n",
    ]
    for it in index:
        flags = ""
        flags += "M" if it["valid_meeting"] else "-"
        flags += "T" if it["has_transcript"] else "-"
        flags += "S" if it["has_panels"] else "-"
        title = it["title"].replace("[", "(").replace("]", ")")
        idx.append(
            f"- {it['date']} {it['time'][:2]}:{it['time'][2:]} `[{flags}]` "
            f"[{title}]({it['fname']})"
        )
    (out / "INDEX.md").write_text("\n".join(idx))

    print(f"      → wrote {written} markdown files ({errors} errors)", flush=True)
    print(f"      → master index: {out / 'INDEX.md'}", flush=True)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Extract Granola.ai personal data via REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST,
                    help=f"Output directory (default: {DEFAULT_DEST})")
    ap.add_argument("--index-only", action="store_true",
                    help="Only fetch document metadata, not transcripts/panels")
    ap.add_argument("--skip-render", action="store_true",
                    help="Skip Markdown rendering (raw JSON only)")
    ap.add_argument("--workers", type=int, default=4,
                    help="Parallel fetchers for transcripts/panels (default: 4)")
    ap.add_argument("--no-extended", action="store_true",
                    help="Skip extended fetch (aux endpoints + attachments). "
                         "By default the extended fetch runs after the core meeting fetch.")
    args = ap.parse_args()

    args.dest.mkdir(parents=True, exist_ok=True)

    # Auth check up front
    try:
        token = load_workos_token()
        user = load_user_info()
        h = hello(token)
        print(f"Authed as {user.get('email', '?')} — {h}", flush=True)
    except TokenError as e:
        print(f"\n❌ Token error: {e}\n", file=sys.stderr)
        print("Try:  ~/.claude/skills/granola-export/scripts/refresh_token.sh\n",
              file=sys.stderr)
        sys.exit(2)
    except ApiError as e:
        print(f"\n❌ API error during auth check: {e}\n", file=sys.stderr)
        sys.exit(2)

    # Step 1: index
    bundle = step_fetch_index(args.dest, token)

    if args.index_only:
        print("\nDone (index only).")
        return

    # Step 2: payloads
    step_fetch_payloads(args.dest, bundle, token, workers=args.workers)

    # Step 2b: extended fetch (aux endpoints + attachments)
    if not args.no_extended:
        step_fetch_aux(args.dest, token)
        step_fetch_attachments(args.dest, bundle)

    # Step 3: render
    if not args.skip_render:
        step_render_markdown(args.dest, bundle)

    print(f"\nDone. Output: {args.dest}")


if __name__ == "__main__":
    main()
