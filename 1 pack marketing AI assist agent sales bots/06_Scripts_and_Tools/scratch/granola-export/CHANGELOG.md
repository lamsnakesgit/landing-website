# Changelog

All notable changes to `granola-export` will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows semantic versioning (loosely — Granola's API isn't versioned, so neither is this).

## [Unreleased]

## [0.1.0]

Initial public release. Built from observing how Granola Mac app v7.155.1 talks to its backend.

### Added

- **Auth**: WorkOS Bearer token loaded from the local `supabase.json` already maintained by the desktop app. Token refresh helper (`refresh_token.sh`) using the WorkOS OAuth2 token endpoint.
- **Document enumeration**: paginated `/v2/get-documents` (offset-based, 100 docs per page).
- **Per-doc fetch**: `/v1/get-document-transcript` and `/v1/get-document-panels`, in parallel via `ThreadPoolExecutor`.
- **Attachments**: walks each doc's inline `attachments` field and downloads the S3-presigned image URLs while the URLs are still fresh.
- **Auxiliary endpoints** (15): folders, recipes, panel templates, people, calendar, integrations, workspace metadata, paywall status, etc.
- **Defensive paid-tier helpers**: `get_action_items`, `get_follow_up_emails`, `get_ambient_context`, `get_about_me_profile`. Auto-graceful-fail with `ApiError` on free-tier accounts; auto-cover paid accounts with no code changes.
- **Markdown rendering**: one file per meeting, full panel detail (including `original_content`, `suggested_questions`, `user_feedback`, `template_slug`), plus a sortable master `INDEX.md`.
- **ProseMirror→Markdown converter** that handles the documented node types plus defensive fallbacks for the `content`-as-string case Granola occasionally returns.
- **Idempotent skip-if-exists** logic: re-running the script tops up new docs without re-fetching old ones.
- **Claude Code skill bundle**: SKILL.md + references/ + examples/ for use as a globally-loadable skill.
- **Test suite** (`tests/test_api.py`): unit tests for `pm_to_md`, `slugify`, `fmt_attendees`, `fmt_transcript`. Pure-function tests, no live API.
- **Issue templates**: bug.yml + api-drift.yml. Blank issues disabled.

### Verified live

Tested against a real Granola account on a free trial. The script:

- Authenticates via the local WorkOS token and confirms identity via `/v1/hello`
- Enumerates documents through the v2 paginated endpoint
- Fetches transcripts and AI summary panels in parallel; both can be empty for some docs (notes without recording, or meetings the user manually deleted) and the script writes an empty result rather than failing
- Downloads inline image attachments while their S3-presigned URLs are valid
- Captures 15 of 16 auxiliary endpoints; the 4 paywalled ones (action items, follow-up emails, ambient context, pre-meeting briefs) return `403 "feature not enabled"` on free tier and are written as JSON error stubs rather than crashing

### Known limitations

- **Audio recordings are not retrievable.** No download endpoint exists in Granola's client codebase — confirmed via static analysis of the asar source. Even Granola's own desktop app cannot replay saved audio.
- **Chat history (Chat with documents).** No discoverable list endpoint via REST. Persisted client-side in `~/Library/Application Support/Granola/IndexedDB/`. Out of scope for this tool; would require a separate IndexedDB-parsing project.
- **Token refresh URL is inferred, not live-verified.** `https://auth.granola.ai/oauth2/token` matches WorkOS's standard OIDC shape, but if it 404s, the script fails gracefully and points users to the desktop-app refresh fallback.
- **macOS only** for the auth-token file path. Windows/Linux would need different paths (PRs welcome).
- **No retry/backoff** on 5xx. If Granola has a brief outage, in-flight requests fail and save error stubs; re-running picks them up.

### Compliance posture

- Tool operates only on the user's own data via the user's own authenticated session
- No bypass of authentication
- No scraping of other users' data
- No modification of Granola's behavior on disk or in transit
- MIT-licensed

[Unreleased]: https://github.com/moona3k/granola-export/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/moona3k/granola-export/releases/tag/v0.1.0
