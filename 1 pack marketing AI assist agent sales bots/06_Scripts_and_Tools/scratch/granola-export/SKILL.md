---
name: granola-export
description: Extract personal data (notes, transcripts, AI summaries, attachments, custom recipes, chat history) from Granola.ai via their undocumented REST API using locally-stored auth tokens. Use when the user wants to back up, recover, snapshot, or export their Granola data — especially after a tier downgrade where the UI hides data the API still serves. Triggers on "export granola", "backup granola", "extract granola data", "recover granola notes", "granola data export", "download my granola meetings". Built from a complete reverse-engineering of Granola Mac app v7.155.1 (April 2026).
---

# Granola Personal Data Export

Extract your own Granola.ai data — meetings, notes, transcripts, AI summaries — via their REST API using the auth tokens stored locally by the Granola Mac app. **For personal data recovery only.** Reads tokens from your already-logged-in session; never logs in or scrapes.

## Why this exists

Granola already has two official ways to get your data out:

- **CSV export** (Settings → Profile → "Generate CSV") — enabled by default on Basic (free) and Business plans, admin-toggle on Enterprise. Returns titles + short summaries only, emailed within hours, rate-limited to 1 per 24h. No transcripts, no AI panel content, no attachments.
- **Personal API** (documented at `docs.granola.ai/introduction`) — `GET /v1/notes`, full notes with transcript + summary as JSON, auth via `grn_` API keys. **Business + Enterprise plans only.**

If you're on Business+ and want JSON note access, **use Granola's official API** — it's the supported path with stable contracts.

This skill fills the gaps neither covers:

- **Free-tier full history.** Basic plan's UI shows only the last 30 days, but the underlying API returns everything. This skill uses that path.
- **Markdown rendering per meeting.** Granola's API returns JSON; this renders one Markdown file per meeting plus a sortable index.
- **Auxiliary data.** Folders, recipes, panel templates, calendar links, attendee profiles — none in `/v1/notes`, all captured here.
- **AI panels with original + edited content.** The full ProseMirror panel content, including the AI's first draft before user edits.
- **Claude Code skill packaging.** Trigger phrases auto-load this skill; AI coding agents can run the export end-to-end.

About audio: **Granola doesn't store audio recordings** — they're transcribed in real time and then deleted, by design (privacy choice). So no tool, including this one, can recover the actual audio file. The `audio_file_handle` field on documents is a vestige of upload processing, not a permanent storage pointer.

Prior art worth knowing: [theantichris/granola](https://github.com/theantichris/granola), [magarcia/granola-cli](https://magarcia.io/reverse-engineered-meeting-notes-into-terminal/), [wassimk/granary](https://github.com/wassimk/granary), [pedramamini/granola-mcp](https://lobehub.com/mcp/pedramamini-granola-mcp), and Joseph Thacker's [Granola → Obsidian writeup](https://josephthacker.com/hacking/2025/05/08/reverse-engineering-granola-notes.html). Different approaches (cache parsing vs. API calls vs. MCP). This skill's differentiators: full Claude Code skill packaging, defensive paid-tier endpoint coverage, idempotent backups.

## Quick start

```bash
# Full export — meetings + transcripts + AI summaries + attachments
# + auxiliary endpoints (folders, recipes, templates, people, etc.)
python3 ~/.claude/skills/granola-export/scripts/extract.py

# Output:
#   ~/reference/granola/extracted/my-data/
#     ├── docs.json                       (all document metadata, 46 fields per doc)
#     ├── transcripts/<id>.json           (raw word-level transcripts)
#     ├── panels/<id>.json                (raw AI summary panels, ProseMirror JSON)
#     ├── attachments/                    (downloaded image attachments)
#     │   ├── _index.json
#     │   └── <attachment-id>.<ext>
#     ├── aux/                            (single-shot auxiliary endpoints)
#     │   ├── recipes.json, panel_templates.json, folders.json,
#     │   │   workspaces.json, people.json, subscription.json, etc. (~16 files)
#     │   └── rendered/*.md               (human-readable summaries)
#     └── meetings/                       (rendered Markdown — one file per meeting)
#         ├── INDEX.md                    (sortable master index)
#         └── YYYY-MM-DD_HHMM_title-slug_<id>.md × N

# To skip the extended fetch (only meetings, no aux/attachments):
python3 scripts/extract.py --no-extended
```

If the access token is stale, the script prints a clear refresh hint. To refresh:

```bash
~/.claude/skills/granola-export/scripts/refresh_token.sh
```

## Auth model (one-page summary)

- **Granola uses WorkOS** for auth. Cognito tokens also appear in `supabase.json` but are legacy and typically long-expired — vestigial from before the WorkOS migration. Use the WorkOS token, not Cognito.
- Tokens live in `~/Library/Application Support/Granola/supabase.json` as **JSON-stringified inner JSON** (`jq -r '.workos_tokens' | jq -r '.access_token'`).
- WorkOS `access_token` TTL: **~1 hour**. Refresh token long-lived.
- Auth header: `Authorization: Bearer <access_token>`.
- All responses are gzipped — always send `Accept-Encoding: gzip` and use `--compressed`.

Full detail: `references/auth.md`.

## Common operations

### Full export (default)
```bash
python3 scripts/extract.py
```

### Resume / top up after a partial run
```bash
python3 scripts/extract.py     # idempotent — skips files already on disk
```

### Single document
```bash
python3 -c "from api import *; t = get_transcript('<doc-id>'); print(t)"
```

### Refresh token without re-running export
```bash
./scripts/refresh_token.sh
```

### Just the document index (no transcripts/panels)
```bash
python3 scripts/extract.py --index-only
```

## Important endpoints (used by this skill)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `https://api.granola.ai/v1/hello` | Auth probe; returns the user's UUID as plain text |
| `POST` | `https://api.granola.ai/v1/get-user-info` | Returns full user record (email, workspace_ids, scopes) |
| `POST` | `https://api.granola.ai/v2/get-documents` | Paginated document list. Body: `{"limit": 100, "offset": N}` |
| `POST` | `https://api.granola.ai/v1/get-document-transcript` | Body: `{"document_id": "<uuid>"}` → array of transcript segments with `start_timestamp`, `text`, `source` (microphone/system) |
| `POST` | `https://api.granola.ai/v1/get-document-panels` | Body: `{"document_id": "<uuid>"}` → array of AI summary panels in ProseMirror JSON |
| `POST` | `https://api.granola.ai/v1/get-feature-flags` | All feature flags for the user (also in `local-state.json`) |
| `POST` | `https://api.granola.ai/v1/get-attachments` | File attachments uploaded into a doc |
| `POST` | `https://api.granola.ai/v1/get-recipes` | Recipes — returns dict with `userRecipes`, `sharedRecipes`, `publicRecipes`, `unlistedRecipes`, `defaultRecipes`, `recipesUsage` |
| `POST` | `https://api.granola.ai/v1/get-panel-templates` | Default + custom panel templates (returns array) |
| `POST` | `https://api.granola.ai/v2/get-document-lists` | Folder/list organization. **v2** — `/v1/get-document-lists` returns "Not implemented" |
| `POST` | `https://api.granola.ai/v1/get-shared-documents` | Documents shared *to* you by others |

Many more exist but are not needed for personal data export. Full curated list in `references/endpoints.md`.

## Known pitfalls

Real failure modes encountered while building this — handled defensively in the bundled scripts, documented here so you understand what's happening if you hit them.

| Symptom | Cause | Fix (already in scripts) |
|---------|-------|--------------------------|
| HTTP 200 but binary garbage in response | Response is gzipped | Always pass `--compressed` to curl, or `Accept-Encoding: gzip` header for libraries that auto-decompress |
| `"error": "deprecated"` | Hitting a v1 endpoint that was superseded | Use `/v2/get-documents` (not `/v1/get-documents-delta`) |
| `"message": "Internal Server Error"` after long timeout | Bare `{}` body where backend expects pagination params | Pass `{"limit": 100, "offset": 0}` |
| `'str' object has no attribute 'get'` in ProseMirror conversion | Some panels have `content` as a bare string instead of a dict | The `pm_to_md()` function in `api.py` handles strings, lists, dicts, and None defensively |
| jq `Invalid string: control characters from U+0000 through U+001F` | Granola's API responses contain raw newlines/tabs in some string fields (notes content) | Don't try to split docs.json with `jq -c '.docs[]'`; iterate via Python instead |
| Token expired | Access token TTL is ~1 hour | Run `scripts/refresh_token.sh` to mint a new one |
| `xargs` workers can't see exported bash functions | xargs spawns a fresh shell that doesn't inherit functions | Write workers as scripts to a file, then `xargs -P 4 worker.sh {}` |
| Empty transcripts (file size = 2 bytes, content `[]`) | The doc had no transcribed audio (you may have disabled transcription, or the doc is a manual note) | Expected; not an error |

## Data shapes (cheat sheet)

**Document** (from `/v2/get-documents`):
```
{ id, created_at, updated_at, deleted_at, title, type, transcribe,
  valid_meeting, public, user_id, cloned_from,
  notes (ProseMirror JSON), notes_markdown (string), notes_plain (string),
  google_calendar_event (object | null), people (object), chapters (null|array),
  meeting_end_count, selected_template, overview }
```

**Transcript segment** (array element):
```
{ document_id, id, start_timestamp, end_timestamp, text,
  source: "microphone" | "system",
  is_final: bool, transcriber_user_id }
```

**Panel** (AI summary, array element):
```
{ document_id, id, created_at, title (string),
  content: ProseMirror JSON document with heading/paragraph/bulletList/listItem nodes }
```

Full detail: `references/data-shapes.md`.

## What this skill does NOT do

- **Does not log you in.** Uses your existing Granola Mac app session. If you're logged out of the app, log back in first.
- **Does not abuse the API.** 4 parallel workers max, per-request timeouts, idempotent skip-if-exists.
- **Does not modify Granola data.** All operations are read-only (`get-*` endpoints).
- **Does not extract other users' data.** Only your own — scoped by your auth token.

## What's NOT recoverable (by Granola's design — verified live)

These were systematically probed and confirmed; flagging them so you don't waste time on them:

- **Audio recordings**. The asar source has zero audio download endpoints — only upload. Granola's own desktop app cannot replay audio. The `audio_file_handle` field is preserved as a reference but the file is not retrievable via API.
- **Chat history (Chat with documents conversations)**. No discoverable list endpoint. Chat threads are persisted client-side in IndexedDB; recovering them would require parsing the local LevelDB at `~/Library/Application Support/Granola/IndexedDB/` — out of scope for this skill.
- **Action items as first-class entities** (`maple/v1/get-action-items`). Server returns `403 "feature not enabled"` on free-trial accounts. They're typically embedded inside the AI summary panels we *do* fetch.
- **Pre-meeting briefs** (`maple/v1/get-pre-meeting-briefs`). Returns `404` for free-trial accounts.
- **Follow-up emails** (`berry/v1/get-follow-up-emails`). Server returns `403`.
- **Ambient context** (`berry/v1/get-ambient-context`). Server returns `403`.

If your account is on a paid tier, the skill will succeed on the paywalled endpoints automatically — no code changes needed; it just stops getting 403s.

## Operating environment

Built and tested on macOS 14+ with Granola Mac app v7.155.1 (April 2026). The auth-token file path is macOS-specific. For Windows/Linux, you'd need to find the equivalent (`%APPDATA%\Granola\` on Windows; the WorkOS auth flow is the same).

## See also

- `references/auth.md` — WorkOS flow + refresh, supabase.json structure, all the gotchas
- `references/endpoints.md` — curated endpoint reference, when to use each
- `references/data-shapes.md` — JSON shapes for every data type
- `examples/output-sample.md` — what a rendered meeting Markdown file looks like (synthetic example)

## Compliance note

This skill operates exclusively on the user's own data, using the user's own authenticated session, against endpoints the Granola desktop app itself calls. Data portability of one's own data is recognized under GDPR Art. 20, CCPA, and similar regimes. The skill does not bypass authentication, scrape other users' data, or violate Granola's ToS in any meaningful sense — it does mechanically what the user could do clicking around the app. **It is the user's responsibility** to ensure their use of extracted data complies with any applicable agreements.

Do not redistribute extracted data, do not embed Granola code or content into derivative products, and do not use this skill against accounts you do not own.
