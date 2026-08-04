# AI Assistant Memory, Context, and Task Routing

## Goal

Build N8 Assistant as an "AI with hands": a Telegram-first assistant that can remember user preferences across sessions, use project documents and artifacts as context, and turn chat messages into structured tasks for specialized workers/subagents.

This is part of the native TypeScript/Next.js architecture. Do not move core orchestration back into n8n unless a workflow is explicitly requested as an external automation.

## Product Shape

The assistant should work in three modes:

1. **Direct chat / DM**
   - Personal assistant experience.
   - Uses the user's long-term memory, system prompt, recent dialogue, files, and connected integrations.
   - Best for private planning, content ideas, drafts, and execution requests.

2. **Group chat / channel / forum topic**
   - Shared workspace experience.
   - Telegram supports this through bot group access and, for forum topics, `message_thread_id`.
   - Each group topic should have its own session and memory scope.
   - The assistant should only respond when mentioned, replied to, or triggered by commands, unless the group explicitly enables always-on mode.

3. **Task dispatcher**
   - User writes rough instructions in chat.
   - Assistant normalizes the request into a structured task.
   - Task is assigned to a specialist route, for example content, research, CRM, scheduling, integrations, or code.
   - Status and outputs are written back to Supabase and optionally echoed to Telegram/Asana.

## Context Sources

The assistant should be able to pull context from:

- Current Telegram message and attachments.
- Recent conversation history.
- Long-term user memory and preferences.
- Project documents and handoff files in this repo.
- Uploaded files and generated artifacts.
- Supabase tables for saved knowledge, task history, integrations, and usage.
- External tools later: Asana, Notion, Google Drive, Gmail, Slack, WhatsApp, Instagram/Meta, YouTube.

For MVP, prioritize Supabase + Telegram + local/project docs. External apps should be connected through explicit integrations after auth is in place.

## Memory Model

Use several memory layers instead of one unstructured chat log:

- **Profile memory:** stable user preferences, tone, language, business context, default output formats.
- **Conversation memory:** recent messages scoped by Telegram chat/session.
- **Knowledge memory:** document chunks, artifacts, briefs, strategies, examples, and reusable notes.
- **Task memory:** created tasks, status changes, decisions, results, links, and handoffs.

Memory writes should be deliberate:

- Do not save every token as a permanent preference.
- Save durable facts only when the user states a preference, business rule, project detail, or reusable context.
- Store raw messages separately from extracted memory.
- Include `source`, `confidence`, and `created_by` fields so bad memories can be audited or deleted.

## Telegram Session Keys

Session identity should be deterministic:

- DM: `telegram:user:{telegram_id}`
- Group without topic: `telegram:chat:{chat_id}`
- Group forum topic: `telegram:chat:{chat_id}:thread:{message_thread_id}`
- Per-user inside group when needed: append `:user:{telegram_id}`

Store Telegram `chat_id`, `message_thread_id`, `telegram_id`, and `session_key` on messages and tasks.

## Group and Topic Behavior

Telegram bots can operate in groups/channels, but behavior depends on BotFather privacy settings and admin permissions.

Recommended defaults:

- DM: respond to all normal user messages.
- Group: respond only on `/ai`, `/task`, direct mention, or reply to bot.
- Topic: use the same trigger rules, but scope memory and tasks to `message_thread_id`.
- Channel: treat as publishing/scheduling surface, not normal chat, unless explicitly configured.

## Task Intake

Every execution-style request should become a task record before work starts.

Minimum normalized task shape:

```json
{
  "title": "Short actionable title",
  "objective": "What done means",
  "source": "telegram",
  "route": "content|research|crm|scheduler|integration|code|general",
  "priority": "low|normal|high|urgent",
  "status": "queued",
  "context": {
    "raw_message": "...",
    "attachments": [],
    "session_key": "telegram:user:123"
  }
}
```

For ambiguous messages, the assistant should either ask one concise clarifying question or create a draft task with `status = needs_clarification`.

## Subagent Routes

Initial routing map:

- `content`: Instagram ideas, carousels, scripts, captions, repurposing.
- `research`: collect context, compare options, summarize sources.
- `crm`: leads, outreach drafts, follow-ups.
- `scheduler`: calendar, posting queue, reminders.
- `integration`: external apps, webhooks, API setup.
- `code`: repo changes, technical fixes, tests.
- `general`: normal assistant response when no specialized route is needed.

In the app, these can start as route labels and server-side handlers. Later they can become real agents, queues, or external workers.

## Content Factory Flow

MVP flow for Instagram/content:

1. User sends messy idea, voice, file, screenshot, or link.
2. Bot transcribes/extracts text if needed.
3. Assistant classifies the intent and pulls profile/project memory.
4. If content-related, create a `content` task.
5. Generate structured brief:
   - topic
   - audience
   - angle
   - hook
   - format: post, carousel, reel, story, thread
   - CTA
   - assets needed
6. Save draft and task status.
7. Return a short answer in Telegram with next action buttons.

## Asana and External Task Tools

Asana should be treated as an optional task mirror, not the source of truth for MVP.

Recommended path:

1. Supabase remains source of truth.
2. `agent_tasks` stores task state.
3. Later integration syncs selected tasks to Asana.
4. Incoming Asana comments can be ingested as task events.
5. The assistant standardizes rough chat instructions before creating/updating Asana tasks.

## Implementation Order

1. Add Supabase schema for memory, knowledge sources, messages, tasks, and task events.
2. Update Telegram text handler to compute `session_key`.
3. Save incoming messages before LLM calls.
4. Build memory retrieval helper:
   - profile memory
   - recent messages
   - relevant knowledge chunks
5. Add task classifier/normalizer.
6. Create task records for execution requests.
7. Add admin/debug view in dashboard for memories and tasks.
8. Add external integrations after auth and task base are stable.

## Non-Goals for MVP

- Fully autonomous multi-agent execution without review.
- Deep Asana/Notion/GDrive sync before Supabase memory works.
- Always-on group monitoring by default.
- Long-term memory writes without source metadata.

