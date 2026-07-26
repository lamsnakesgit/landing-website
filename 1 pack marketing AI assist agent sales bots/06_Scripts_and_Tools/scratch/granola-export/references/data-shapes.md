# Granola Data Shapes — Reference

> JSON shapes for every Granola data type relevant to personal export. Derived from observing live API responses on a real Granola account.

## Document (from `/v2/get-documents`)

The listing endpoint returns **46 fields per doc**. Below in two groups: the ones you'll actually look at, and the long tail of state flags. Note: `/v1/get-document` returns 404 — there is no per-doc fetch endpoint; the listing is canonical.

### Primary fields (the ones that matter for export)
```json
{
  "id": "0066c654-8fc6-4244-abd0-f53aa895dff3",
  "user_id": "<your uuid>",
  "workspace_id": "<workspace uuid>",
  "created_at": "2026-04-01T17:02:16.205Z",
  "updated_at": "2026-04-01T17:48:32.119Z",
  "deleted_at": null,                      // server-side soft-delete (almost never set)
  "title": "Weekly sync",                  // user-editable; AI-generated when transcribed
  "type": "meeting" | null,                // null = standalone note
  "valid_meeting": true,                   // Granola's own meeting-vs-noise classifier
  "transcribe": false,                     // currently-active flag, NOT "has transcript"
  "public": false,
  "people": { /* see below */ },
  "google_calendar_event": { /* see below */ } | null,
  "notes": { /* ProseMirror JSON document */ },
  "notes_plain": "follow-up next week\n",  // user's own notes, plain text
  "notes_markdown": "follow-up next week\n",
  "attachments": [ /* see below — inline image attachments */ ],
  "audio_file_handle": "<user-id>/<doc-uuid>.m4a" | null,  // upload-pipeline vestige; Granola doesn't persist audio
  "external_transcription_id": "<uuid>" | null,
  "status": "ready" | null,
  "creation_source": "auto_calendar" | "manual" | ...,
  "privacy_mode_enabled": false,           // user marked the recording private
  "subscription_plan_id": "granola.plan.free-trial.v1"
}
```

### State / flag fields (rarely needed for export but present)
```json
{
  "cloned_from": null,                     // UUID if doc is a copy
  "is_primary_event_note": false,
  "is_scratchpad": false,
  "was_trashed": false,
  "transcript_deleted_at": null,           // user-triggered transcript delete
  "selected_template": null,               // panel template ID for AI summary
  "overview": null,
  "summary": null,                         // (always null in observed data; summaries live in panels)
  "chapters": null,                        // chapter generation (paywalled)
  "meeting_end_count": 1,                  // pause/resume counter
  "last_indexed_at": "<iso>",              // search index sync state
  "sharing_link_visibility": "private",
  "show_private_notes": true,
  "visibility": null,
  "notification_config": null,
  "metadata": null,
  "has_shareable_link": false,
  "ydoc_state": { "type": "Buffer", "data": [...] } | null,  // Yjs CRDT state
  "ydoc_version": 1 | 2 | null,
  "zoom_rtms_permission": null,            // Zoom Realtime Media SDK state
  "hubspot_note_url": null,                // HubSpot integration sync state
  "affinity_note_id": null,                // Affinity integration sync state
  "attio_shared_at": null                  // Attio integration sync state
}
```

**Field semantic gotchas**:

| Field | Meaning |
|-------|---------|
| `transcribe` | Whether transcription is *currently active*. Does NOT mean "has transcript" — historic transcribed meetings show `false` |
| `valid_meeting` | True if Granola classifies the doc as a real meeting (not test/demo). Useful filter |
| `audio_file_handle` | Looks like an S3 key but **does not point to a persistently stored file** — Granola transcribes audio in real time and deletes it, by design (privacy choice). This field is a processing-pipeline vestige, not a storage pointer. There's no audio to retrieve regardless of tooling. |
| `deleted_at` | Almost never set — Granola does soft-delete in the UI but rarely persists `deleted_at` server-side. Free-tier downgrades are UI-only |
| `summary` | Always null in observed data. AI summaries live in the separate `panels` resource, not on the doc |

**Field semantics** (the non-obvious ones):

| Field | Meaning |
|-------|---------|
| `transcribe` | Whether transcription was *active* at fetch time. Does NOT mean "has transcript" — meetings transcribed in the past have `transcribe: false` but full transcripts are still retrievable |
| `valid_meeting` | True if Granola considers this a real meeting (vs. a quick note, demo, or test). Useful filter |
| `type` | `"meeting"` or `null`. Null = standalone note, not associated with a calendar event |
| `meeting_end_count` | How many times the meeting was ended. Higher than 1 means user paused/restarted |
| `cloned_from` | UUID if this doc is a clone of another. Mostly null |
| `notes` | ProseMirror JSON — same content as `notes_markdown` but in their structured editor format |
| `notes_plain` | Whitespace-normalized plaintext of the user's notes |
| `notes_markdown` | Markdown rendering of the user's notes |
| `public` | True if the doc is publicly shareable via link |
| `deleted_at` | Soft-delete timestamp. **Granola almost never hard-deletes** — even free-tier downgrades just hide; the record stays |

## Transcript (array from `/v1/get-document-transcript`)

The endpoint returns a **bare JSON array** (not wrapped in an object). Each element:

```json
{
  "document_id": "<uuid>",
  "id": "e7d1d21f-f7ab-48e5-aa0d-e7fadb887027",
  "start_timestamp": "2025-06-17T19:02:29.419Z",
  "end_timestamp": "2025-06-17T19:02:31.119Z",
  "text": "Oh, I'm trying to figure out how to document all this",
  "source": "microphone" | "system",
  "is_final": true,
  "transcriber_user_id": null
}
```

| Field | Meaning |
|-------|---------|
| `source` | **`microphone`** = your mic input, **`system`** = system audio capture (other meeting participants via ScreenCaptureKit/Core Audio Taps). This is real diarization data |
| `is_final` | True for committed transcript; false for streaming intermediate hypotheses (almost always filtered server-side; you'll see all `true` in saved data) |
| `transcriber_user_id` | The user who triggered the transcription (relevant for shared meetings). Null for self-transcribed |
| Sort order | Returned sorted by `start_timestamp` ascending; safe to assume that |
| Empty transcripts | Returned as `[]`. Plus a few documents have errors saved as `{"error": "..."}` if a server hiccup occurred |

**Audio source distinction is gold.** Most STT pipelines lose this; Granola preserves it because they capture the two streams separately and tag each segment with which stream it came from. Useful for:
- Filtering "what I said" vs "what they said"
- Identifying who's speaking in a 1:1 (your mic = you; system audio = the other person)
- Detecting cross-talk

## Panel (AI summary, array from `/v1/get-document-panels`)

```json
{
  "document_id": "<uuid>",
  "id": "3b1896d9-00de-41bb-978c-a65552d8af2a",
  "created_at": "2025-06-17T20:26:56.228Z",
  "updated_at": "2025-06-17T22:00:00.000Z",
  "deleted_at": null,
  "title": "Summary",
  "content": { /* ProseMirror JSON document — current state */ },
  "original_content": { /* ProseMirror JSON — pre-user-edit AI version */ },
  "template_slug": "default-summary",
  "generated_lines": null,
  "suggested_questions": [
    "What was the main blocker discussed?",
    "Who owns the follow-up?"
  ],
  "user_feedback": null | "thumbs_up" | "thumbs_down",
  "content_updated_at": "2025-06-17T22:00:00.000Z",
  "last_viewed_at": "2025-06-18T09:14:00.000Z",
  "ydoc_version": null,
  "affinity_note_id": null
}
```

A panel is a **structured AI-generated output** — typically a multi-section summary (action items, key decisions, etc.). The `title` is the panel's heading ("Summary", "Action Items", "Key Decisions", etc.). Panels can come from:
- The default summary template Granola ships
- A custom recipe the user defined
- A panel template selected for this meeting

Field semantics worth knowing:

| Field | Notes |
|-------|-------|
| `content` | Current state — what the user sees in the UI. May reflect their edits. |
| `original_content` | The AI's first generation, before any user edits. Often differs from `content` on edited summaries; useful if you want to see what the AI proposed. |
| `template_slug` | Which template generated this panel. Maps to entries in `panel_templates.json` |
| `suggested_questions` | AI-suggested follow-up questions based on the meeting. May be string-array or object-array; handle both |
| `user_feedback` | If the user thumbed up/down the summary |
| `generated_lines` | Sometimes set to mark which lines are AI-generated vs user-typed (often null) |

`content` is **usually** a ProseMirror document (root node `{type: "doc", content: [...]}`). **Defensive note**: a non-trivial fraction of panels arrive with `content` as a bare string instead of a node tree. The `pm_to_md()` function handles both.

## ProseMirror JSON

Granola uses ProseMirror's standard schema. Node types you'll encounter:

| Type | Notes |
|------|-------|
| `doc` | Root node. `content` is a list of block nodes |
| `heading` | `attrs.level` (1-6). `content` has inline nodes |
| `paragraph` | `content` has inline nodes |
| `bulletList`, `orderedList` | Each item is a `listItem` |
| `listItem` | Contains paragraph/list content |
| `codeBlock` | `attrs.language` optional |
| `blockquote` | Wraps block content |
| `text` | Inline. `text` is the literal string. `marks` array contains formatting |
| `hardBreak` | Inline. Renders as `\n` in markdown |

`marks` on a `text` node:

| Mark type | Meaning |
|-----------|---------|
| `bold` | `**text**` |
| `italic` | `*text*` |
| `code` | `` `text` `` |
| `link` | `attrs.href` |

The `pm_to_md()` function in `scripts/api.py` handles all of these.

**Defensive note:** sometimes a panel's `content` arrives as a bare string instead of a node tree. (We hit this on roughly 1 in 5 panels.) Always handle the `isinstance(node, str)` case in any ProseMirror walker. The bundled `pm_to_md()` does this.

## Google Calendar event (embedded in document)

When a document is linked to a Google Calendar event:

```json
{
  "id": "abc123_20250607T140000Z",
  "summary": "Sprint review",
  "description": "Agenda: ...",
  "start": { "dateTime": "2025-06-07T14:00:00-07:00", "timeZone": "America/Los_Angeles" },
  "end":   { "dateTime": "2025-06-07T15:00:00-07:00", "timeZone": "America/Los_Angeles" },
  "attendees": [
    { "email": "alice@example.com", "displayName": "Alice", "responseStatus": "accepted", "self": false, "organizer": true },
    { "email": "bob@example.com",   "displayName": "Bob",   "responseStatus": "accepted", "self": false }
  ],
  "organizer": { "email": "alice@example.com", "self": false },
  "creator": { "email": "alice@example.com" },
  "conferenceData": {
    "conferenceSolution": { "name": "Google Meet" },
    "entryPoints": [{ "uri": "https://meet.google.com/abc-defg-hij", "entryPointType": "video" }]
  },
  "htmlLink": "https://calendar.google.com/event?eid=...",
  "hangoutLink": "https://meet.google.com/abc-defg-hij"
}
```

The same shape applies for Outlook calendar events when synced through Granola's adapter.

## People (attendee tracking on a document)

```json
{
  "organizer": { "email": "...", "displayName": "..." } | null,
  "attendees": [
    { "email": "...", "displayName": "...", "responseStatus": "accepted", "self": false, "person_id": "<uuid>" },
    ...
  ],
  "manual_attendee_edits": [
    { "action": "add" | "remove", "email": "...", "displayName": "..." }
  ]
}
```

`manual_attendee_edits` captures user overrides — e.g. you join a meeting that wasn't on calendar and manually add the person you met with.

## Recipes (from `/v1/get-recipes`)

Returns a **dict** with categorized lists (not a flat array):

```json
{
  "userRecipes":     [],     // recipes you authored
  "sharedRecipes":   [],     // recipes shared with you / your workspace
  "publicRecipes":   [...],  // community library — typically the largest list (50+)
  "unlistedRecipes": [],
  "defaultRecipes":  [],     // Granola-curated defaults
  "recipesUsage":    { "<recipe-slug>": {...usage stats...} }
}
```

Each recipe element:
```json
{
  "id": "<uuid>",
  "slug": "follow-up-email",
  "user_id": "<uuid> | null",
  "workspace_id": "<uuid> | null",
  "config": {
    "title": "Follow-up email",
    "description": "Drafts a follow-up email",
    /* ...sections, prompts (often stripped server-side), icon, etc. */
  },
  "created_at": "...",
  "updated_at": "...",
  "deleted_at": null
}
```

**Note**: the `prompt` body is often empty/stripped in API responses. Granola injects prompts server-side when actually generating a summary; the client only sees recipe metadata. If you want to see actual prompts, that's not retrievable via REST.

## Panel Template (from `/v1/get-panel-templates`)

Returns a **flat array** of templates — Granola-built defaults plus any user-created custom ones. The defaults cover common categories (Leadership, Team, VC, Recruiting, Commercial). Each entry:

```json
{
  "id": "<uuid>",
  "owner_id": "<user-uuid> | null",   // null for Granola-built defaults
  "is_granola": true | false,         // true = ships with the app
  "category": "Leadership" | "Team" | "VC" | "Recruiting" | "Commercial" | null,
  "title": "Board Meeting" | "Stand-Up" | ...,
  "slug": "board-meeting",
  "sections": [
    {
      "heading": "Key Decisions",
      "description": "Decisions made during the meeting",
      "instructions": "<LLM instructions, often stripped on free tier>"
    }
  ],
  "created_at": "...",
  "deleted_at": null
}
```

## Folder / List (from `/v2/get-document-lists`)

Returns `{"lists": [...]}`. Each list:

```json
{
  "id": "<uuid>",
  "title": "Customer Calls",
  "user_id": "<uuid>",
  "workspace_id": "<uuid> | null",
  "document_ids": ["<doc-uuid>", ...],
  "icon": "📞" | null,
  "created_at": "...",
  "updated_at": "...",
  "shared_with": [...]
}
```

## Inline Attachment (within a document's `attachments` field)

```json
{
  "id": "<attachment-uuid>",
  "url": "https://granola-attachments.s3.amazonaws.com/...?X-Amz-Signature=...",
  "type": "image",
  "width": 1234,
  "height": 567
}
```

The `url` is **S3-presigned with a short TTL** (typically minutes to hours). Download immediately on receipt; don't cache the URL.

## Recipe / Panel Template (legacy single-item shape, returned from `/v1/get-document` if it ever worked)

Below is the shape some older Granola docs reference. The per-doc fetch endpoint currently returns 404 and these shapes aren't actually used — kept here for completeness only.

```json
{
  "id": "<uuid>",
  "user_id": "<uuid>",
  "title": "Action Items",
  "description": "Extract action items with owners and due dates",
  "prompt": "<the actual LLM prompt — server-side until executed>",
  "created_at": "...",
  "updated_at": "...",
  "is_default": false,
  "shared": false,
  "panel_template_id": "<uuid> | null"
}
```

## Action Item (from `maple.api.granola.ai/v1/get-action-items`)

```json
{
  "id": "<uuid>",
  "document_id": "<uuid>",
  "text": "Schedule follow-up with Bob next week",
  "owner_email": "you@example.com" | null,
  "due_date": "2025-06-14" | null,
  "status": "open" | "completed" | "dismissed",
  "extracted_at": "...",
  "reviewed_at": "..." | null,
  "review_outcome": "accepted" | "edited" | "rejected" | null
}
```

## Document List (folder)

```json
{
  "id": "<uuid>",
  "title": "Customer Calls",
  "icon": "<emoji>" | null,
  "user_id": "<uuid>",
  "workspace_id": "<uuid>" | null,
  "created_at": "...",
  "shared_with": [...],
  "documents": [{ "document_id": "<uuid>", "added_at": "..." }]
}
```

## Attachment

```json
{
  "id": "<uuid>",
  "document_id": "<uuid>",
  "filename": "screenshot.png",
  "mime_type": "image/png",
  "size_bytes": 524288,
  "created_at": "...",
  "url": "https://granola-uploads.s3.amazonaws.com/...?X-Amz-Signature=..."
}
```

The `url` is **S3-presigned with a short TTL** (typically minutes to hours). Download immediately; don't cache the URL.

## User info (from `/v1/get-user-info`)

```json
{
  "id": "<uuid>",
  "email": "you@example.com",
  "user_metadata": { "name": "..." },
  "signed_in_on_platforms": { "macos": true, "windows": false, "ios": true },
  "signup_platform": null,
  "google_ads_click_id": null,
  "facebook_ads_click_id": null,
  "dub_id": null,
  "created_at": "2025-04-27T06:13:49.581Z",
  "has_valid_web_scopes": false,
  "has_meet_media_api_scope": false,
  "zoom_id": null,
  "person": { "id": "<uuid>", "created_at": "...", "user_id": "<uuid>" },
  "workspace_ids": ["<workspace-uuid>"]
}
```

## Feature flags (from `/v1/get-feature-flags` or `local-state.json`)

A flat object with ~295 boolean/string/number/object values. See `~/reference/granola/findings/raw/feature_flags.txt` for the full inventory. The most operationally relevant ones:

| Key | Type | Meaning |
|-----|------|---------|
| `core_audio` | bool | Audio capture uses Core Audio Taps (vs. ScreenCaptureKit) |
| `transcription_provider` | string | Active STT vendor for this user (`"assembly-universal"`, `"deepgram-nova-3"`, etc.) |
| `transcription_retention_time_ms` | number | Server-side retention for raw transcript chunks (default 259200000 = 3 days) |
| `data_export_enabled` | bool | Whether export is allowed for this account |
| `mcp_enabled` | bool | MCP server access enabled for this user |
| `tpuf_search_enabled` | bool | TurboPuffer semantic search active |
| `inactivity_auto_stop` | object | `{"timeoutMs": 900000}` — 15 min idle = auto-stop |
| `posthog_api_key` | string | PostHog write key (public-by-design) |
| `subscription_plan_id` | string | e.g. `"granola.plan.free-trial.v1"` |

Reading these is useful for understanding what features are wired up for *your* account specifically — server flags can differ between users for A/B tests, regional rollouts, and tier-gated features.

## Things you'll see in responses but probably don't need

- `external_id`, `dub_id`, `*_click_id` — marketing attribution, useless for export
- `signed_in_on_platforms` — UX state
- `has_meet_media_api_scope` — boolean for the Zoom/Meet integration scope
- Timestamp fields ending in `_at` are always ISO-8601 UTC; just parse and forget
