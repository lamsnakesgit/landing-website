# Granola REST Endpoints — Curated Reference

> Endpoint reference for the operations relevant to personal data export. Granola's full surface is ~230 v1 endpoints across `api`, `berry`, `chia`, `cinnamon`, `maple`, `pecan` sub-services plus a streaming gateway and public MCP. Most of those are SaaS scaffolding (workspaces, billing, integrations) and not relevant to extraction.

## Conventions

- Method: **POST** for almost everything (even read-only listing endpoints — Granola treats POST as their default verb)
- Auth: `Authorization: Bearer <workos-access-token>` on every call
- Content type: `application/json` request bodies, `application/json` responses (gzipped)
- Pagination: `{"limit": N, "offset": M}` for `/v2/get-documents`; cursor or batch-by-IDs for some others
- Error shape: `{"message": "<human-readable>"}` for 5xx, `{"error": "<code>"}` for handled 4xx
- Bases:
  - `https://api.granola.ai` — primary (most endpoints)
  - `https://stream.api.granola.ai` — streaming (LLM proxy, summaries)
  - `https://berry.api.granola.ai`, `chia`, `cinnamon`, `maple`, `pecan` — themed sub-services
  - `https://mcp.granola.ai/mcp` — public MCP server
- All endpoints documented in this file are observable from the Granola Mac app's network calls or its bundled JS source

## Auth probes

| Method | Endpoint | Body | Returns | Notes |
|--------|----------|------|---------|-------|
| POST | `/v1/hello` | `{}` | Plain text: `hello <user-id>` | Cheapest auth probe |
| POST | `/v1/get-user-info` | `{}` | Full user record (JSON) | Email, id, workspace_ids, scopes |
| POST | `/v1/get-feature-flags` | `{}` | All ~295 feature flags as a flat object | Same content as `local-state.json` |

## Documents (the core of personal data)

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v2/get-documents` | `{"limit": 100, "offset": 0}` | `{"docs": [...], "deleted": [...]}` |
| POST | `/v1/get-document-transcript` | `{"document_id": "<uuid>"}` | Array of transcript segments |
| POST | `/v1/get-document-panels` | `{"document_id": "<uuid>"}` | Array of AI summary panels (ProseMirror JSON) |
| POST | `/v1/get-document` | `{"document_id": "<uuid>"}` | Single document (richer than the list version) |
| POST | `/v1/get-document-set` | `{"document_id": "<uuid>"}` | Bundle: doc + transcript + panels + attachments in one call |
| POST | `/v1/get-document-metadata` | `{"document_id": "<uuid>"}` | Lightweight metadata only |
| POST | `/v1/get-document-status` | `{"document_id": "<uuid>"}` | Processing status |

**Pagination notes** for `/v2/get-documents`:

- `next_cursor` and `has_more` fields are present but currently `null` in responses — pagination is offset-based today, not cursor-based
- Full enumeration: increment offset by `limit` until you get fewer than `limit` records back
- Tested up to ~1000 docs without issue
- Approximate rate: 100 docs in ~200ms gzipped (~12 KB compressed)

**Deprecated endpoints to avoid:**

- `/v1/get-documents` (without v2) — returns 500 with bare body, requires unknown params
- `/v1/get-documents-delta` — returns `{"error": "deprecated"}`. Use `/v2/get-documents` with offset instead

## Attachments

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/get-attachments` | `{"document_id": "<uuid>"}` | Array of attachment metadata (S3 URLs etc.) |

The attachment URLs returned will likely be S3-presigned with short TTLs. Download immediately on receipt — don't cache the URL.

## Audio

**Granola does not store audio recordings.** Audio is transcribed in real time and then deleted — a deliberate privacy choice on Granola's part, called out in their reviews and product positioning. So there's no audio to recover regardless of account tier or tooling.

The `audio_file_handle` field that appears on document records (typically formatted like `<user-id>/<doc-uuid>.m4a`) is a vestige of the upload-then-transcribe processing pipeline, not a pointer to a persistently stored audio file. The asar source consequently has only upload-side endpoints; there is no GET path because nothing is stored to GET.

If you need an actual audio file, the answer is to record it yourself with a separate tool. Granola's design specifically avoids holding audio for you.

Upload endpoints (for reference, not relevant to export):

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/request-audio-upload-url` | … | Presigned URL for upload |
| POST | `/v1/initiate-multipart-audio-upload` | … | Multipart upload init |
| POST | `/v1/complete-multipart-audio-upload` | … | Finalize multipart |

## AI features

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/get-recipes` | `{}` | Recipes — dict with `userRecipes`, `sharedRecipes`, `publicRecipes`, `unlistedRecipes`, `defaultRecipes`, `recipesUsage` |
| POST | `/v1/get-panel-templates` | `{}` | Array of panel templates (defaults + user-custom) |
| POST | `/v1/get-chat-models` | `{}` | Available LLM models for chat |
| POST | `stream.api.granola.ai/v1/generate-summary` | `{"document_id": ..., ...}` | Streaming SSE summary generation |
| POST | `stream.api.granola.ai/v1/chat-with-documents` | `{...}` | Streaming RAG chat |
| POST | `stream.api.granola.ai/v1/pre-meeting-brief` | `{"calendar_event_id": ...}` | Streaming brief generation |
| POST | `/v1/get-chat-citation` | `{"citation_id": ...}` | Resolve a citation |

## Folders / lists

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v2/get-document-lists` | `{}` | `{"lists": [...]}` — **canonical**. **`/v1/get-document-lists` returns "Not implemented"** — always use v2. |
| POST | `/v1/get-document-list` | `{"list_id": "<uuid>"}` | One list with documents |
| POST | `/v1/get-folder-digest` | `{"folder_id": "<uuid>"}` | AI-generated folder digest (paywalled on free tier) |

## Calendar

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/get-google-events` | `{}` | Google calendar events synced to Granola |
| POST | `/v1/refresh-google-events` | `{}` | Force refresh |
| POST | `/v1/get-selected-calendars` | `{}` | Which calendars are subscribed |
| POST | `/v1/refresh-calendar-events` | `{}` | Cross-provider refresh |
| POST | `maple.api.granola.ai/v1/get-pre-meeting-briefs` | `{}` | Pre-meeting brief inventory |

## Action items (separate entity, on `maple` sub-service)

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `maple.api.granola.ai/v1/get-action-items` | `{}` | All extracted action items |
| POST | `chia.api.granola.ai/v1/update-action-item` | `{"id": ..., ...}` | Update action item state |

## People

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `pecan.api.granola.ai/v1/get-people` | `{}` | People you've met with (extracted from attendee lists) |
| POST | `berry.api.granola.ai/v1/get-about-me-profile` | `{"person_id": "<uuid>"}` | AI-generated person profile |

## Sharing

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/get-shared-documents` | `{}` | Documents shared *to* you |
| POST | `/v1/get-users-with-access` | `{"document_id": ...}` | Who has access to a doc |
| POST | `/v1/check-document-access` | `{"document_id": ...}` | Boolean access check |

## Workspace

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/get-workspaces` | `{}` | Workspaces you're a member of |
| POST | `/v1/get-workspace-members` | `{"workspace_id": ...}` | Member list |
| POST | `/v1/get-current-subscription` | `{}` | Plan + billing state |

## Search

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/search-embeddings` | `{"query": "...", "limit": 10}` | Semantic search over your docs |
| POST | `/v1/search-meetings-turbopuffer` | `{"query": "..."}` | Direct TurboPuffer query |

(The `tpuf_search_enabled` flag controls whether the second one is wired up for your account.)

## MCP server (cloud)

Granola exposes an MCP server at `https://mcp.granola.ai/mcp` so external agents can read your data. Auth via separate MCP token issued by `/v1/manage-mcp-token`. Not strictly necessary for personal extraction (the regular API does the same things) but worth knowing about if you want to integrate with Claude Code, Cursor, or similar agent tools.

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/v1/manage-mcp-token` | `{...}` | CRUD on MCP tokens |
| POST | `/v1/mcp-info` | `{}` | Server metadata |
| POST | `/v1/mcp-registry` | `{}` | Tool registry / discovery |
| POST | `/v1/mcp-tool-execute` | `{...}` | Execute a tool |

## Test endpoints (yes, in production)

These are real endpoints that ship in their production app. Useful for synthetic monitoring; **don't call them as part of normal extraction**:

| Endpoint | Returns |
|----------|---------|
| `/v1/test-400` | Forces a 400 response |
| `/v1/test-500` | Forces a 500 response |
| `/v1/test-exception` | Throws server-side exception |
| `/v1/test-call-sns` | Tests their SNS notification pipeline |

## Things that look like endpoints but aren't (gotchas)

| URL | What it actually is |
|-----|---------------------|
| `https://amp.granola.ai/2/httpapi` | Amplitude product analytics — not Granola's own API |
| `https://api-sr.amplitude.com/sessions/v2/track` | Amplitude session replay — third-party |
| `https://stream.api.granola.ai/v1/llm-proxy-stream` | LLM proxy — used internally for AI features, not for personal data fetch |

## Rate limits (observed, not documented)

No rate limits were hit during testing with 4 parallel workers issuing several thousand requests within a few minutes. Reasonable thresholds based on typical SaaS:
- ~10 req/s sustained should be safe
- Bursting to 50+ likely OK for short periods
- The desktop app itself likely peaks at 5-10 req/s during initial sync

If you do hit a 429 or sudden 5xx wall: back off, slow your concurrency to 1-2 workers, and add a `time.sleep(0.5)` between calls.

## Endpoints we discovered but didn't call

A few hundred endpoints exist that aren't covered above. Pattern-match by topic in the full inventory:

- Integrations (Slack/Notion/HubSpot/Salesforce/Affinity/Attio/Airtable/Zapier): `/v1/<provider>-*`
- Phone calling (Twilio): `/v1/phone-*`
- Stripe billing: `/v1/stripe-*`, `/v1/create-subscription`, etc.
- Knock notifications: `/v1/knock-*`
- Loops email marketing: `/v1/loops-webhook-handler`
- Public website / shortlinks: `/v1/static-assets`, `go.granola.ai/*`

For personal data export, the endpoints above this section are sufficient.
