# Zoom / Fathom Post-Meeting AI Assistant — Architecture Spec

## 1. Goal

Собрать надежного post-meeting ассистента, который после Zoom/Fathom созвона принимает данные из нескольких источников и автоматически выдает 3 результата:

1. **Meeting Summary** — саммари, таймкоды, решения, договоренности, next steps.
2. **Sales Analysis** — анализ продающей встречи: этап сделки, боли, objections, путь клиента, риски, follow-up draft.
3. **Content Repurposing** — Telegram/Instagram пост + серия сторис на основе разговора.

Система должна работать даже если **Fathom webhook не сработал**, через fallback-механику polling/cron.

---

## 2. Main Principles

- **Webhook-first, cron-second**: сначала ловим события, потом добираем пропуски по расписанию.
- **Normalized event layer**: все входящие события приводим к одной схеме.
- **Fast ACK**: webhook отвечает быстро, без тяжелой LLM-обработки в синхронном запросе.
- **Idempotency**: один и тот же ивент не должен запускать дубль обработки.
- **Source of truth**: сначала собираем каноническую структуру встречи, потом уже запускаем субагентов.
- **Strict JSON from LLM**: каждый агент обязан отдавать структурированный JSON.
- **Human-review optional**: можно включить режим черновиков перед публикацией.

---

## 3. Input Sources

### Primary sources
- **Fathom webhook**
- **Zoom webhook**
- **n8n chat input**
- **Telegram audio**
- **Telegram text**

### Optional future sources
- Notion meeting notes
- Google Drive transcript files
- Manual Fathom share link input
- CRM context (HubSpot / Amo / Bitrix)

---

## 4. Unified Input Contract

Все входящие данные приводятся к этому объекту:

```json
{
  "source": "fathom|zoom|telegram_audio|telegram_text|n8n_chat|manual",
  "source_event_id": "string",
  "meeting_id": "string",
  "conversation_id": "string",
  "event_type": "meeting.completed|transcript.ready|chat.received|audio.received|manual.import",
  "occurred_at": "2026-04-15T10:00:00Z",
  "title": "string",
  "host_email": "string",
  "participants": [
    {
      "name": "string",
      "email": "string",
      "role": "host|guest|unknown"
    }
  ],
  "language": "ru",
  "transcript_text": "string",
  "transcript_segments": [
    {
      "speaker": "string",
      "start_sec": 0,
      "end_sec": 12,
      "text": "string"
    }
  ],
  "chat_messages": [
    {
      "timestamp": "2026-04-15T10:10:00Z",
      "author": "string",
      "text": "string"
    }
  ],
  "audio_url": "string",
  "recording_url": "string",
  "metadata": {},
  "raw_payload": {}
}
```

---

## 5. Target Outputs

### 5.1 Summary package
- short summary
- detailed summary by sections
- decisions
- action items
- next steps
- open questions
- timestamps / timecodes

### 5.2 Sales package
- meeting type
- deal stage
- customer pains
- desired outcomes
- objections
- buying signals
- stakeholders
- commitments
- risks
- recommended next move
- follow-up draft

### 5.3 Content package
- Telegram post
- Instagram caption
- 5–8 stories frames
- hooks/headlines
- CTA
- sensitive-info flags

---

## 6. High-Level Architecture

### Workflow A — Webhook Receiver
Задача: быстро принять входящее событие и сохранить raw event.

**Nodes:**
1. `Webhook: fathom_receiver`
2. `Webhook: zoom_receiver`
3. `Set/Code: normalize_event`
4. `Data Store / Supabase: save_raw_event`
5. `Respond 200 OK`

**Important:**
- не запускать LLM прямо тут
- отвечать за 1–3 секунды
- сохранять `raw_payload`

### Workflow B — Event Router / Orchestrator
Задача: определить, хватает ли данных для запуска обработки.

**Logic:**
- если пришел только `meeting.completed`, но еще нет transcript → статус `awaiting_artifacts`
- если transcript уже есть → создать job `process_meeting`
- если event дубликат → игнор

### Workflow C — Artifact Recovery Poller
Задача: компенсировать сбой вебхука.

**Trigger:** каждые 10–15 минут.

**Logic:**
- искать встречи со статусами:
  - `awaiting_artifacts`
  - `webhook_missed`
  - `processing_failed`
- опрашивать Fathom/Zoom API
- добирать transcript / recording / metadata
- переводить встречу в `ready_for_ai`

### Workflow D — AI Processing Pipeline
Задача: собрать каноническую структуру встречи и прогнать 3 субагента.

**Steps:**
1. fetch normalized meeting data
2. transcript cleanup / chunking
3. run `meeting_structurer`
4. run `sales_analyst`
5. run `content_repurposer`
6. JSON validation / repair
7. store results
8. send outputs to Telegram / n8n chat / CRM

### Workflow E — Delivery / Review Layer
- Telegram delivery
- n8n chat delivery
- optional manual approval before publishing content
- logging and status updates

---

## 7. Suggested Storage Schema

### `meeting_events_raw`
- id
- source
- source_event_id
- meeting_id
- event_type
- occurred_at
- payload_json
- idempotency_key
- created_at

### `meetings`
- id
- source
- external_meeting_id
- title
- host_email
- started_at
- ended_at
- status
- language
- transcript_ready
- chat_ready
- recording_ready
- summary_ready
- sales_ready
- content_ready
- error_message
- updated_at

### `meeting_artifacts`
- id
- meeting_id
- transcript_text
- transcript_segments_json
- chat_json
- recording_url
- audio_url
- participants_json
- metadata_json

### `meeting_outputs`
- id
- meeting_id
- summary_json
- sales_analysis_json
- content_json
- delivery_status
- approved_by_human
- created_at

### `processing_jobs`
- id
- meeting_id
- job_type
- status
- attempts
- last_error
- next_retry_at

---

## 8. Idempotency Rules

Использовать ключ:

```text
{source}:{source_event_id}
```

Если `source_event_id` нет:

```text
{source}:{meeting_id}:{event_type}:{occurred_at_rounded}
```

Дополнительно:
- не запускать `process_meeting`, если уже есть job со статусом `queued|running`
- не отправлять одинаковый summary дважды в Telegram

---

## 9. Recommended Status Model

```text
new
received
awaiting_artifacts
ready_for_ai
processing
processed
delivery_pending
delivered
failed
needs_review
```

---

## 10. The 3 Subagents

### Agent 1 — `meeting_structurer`
**Role:** canonical summary builder.

**Input:** transcript, segments, participants, metadata, chat.

**Output JSON:**
```json
{
  "meeting_title": "string",
  "one_paragraph_summary": "string",
  "key_topics": ["string"],
  "decisions": ["string"],
  "action_items": [
    {
      "owner": "string",
      "task": "string",
      "deadline": "string|null"
    }
  ],
  "next_steps": ["string"],
  "open_questions": ["string"],
  "timeline": [
    {
      "timecode": "00:12:40",
      "topic": "string",
      "summary": "string"
    }
  ],
  "confidence_notes": ["string"]
}
```

### Agent 2 — `sales_analyst`
**Role:** revenue-focused analysis of the call.

**Input:** transcript + output of meeting_structurer + optional CRM context.

**Output JSON:**
```json
{
  "meeting_type": "discovery|demo|follow_up|closing|support|unknown",
  "deal_stage": "string",
  "customer_pains": ["string"],
  "desired_outcomes": ["string"],
  "objections": ["string"],
  "buying_signals": ["string"],
  "stakeholders": [
    {
      "name": "string",
      "role": "string",
      "influence": "high|medium|low"
    }
  ],
  "agreements": ["string"],
  "risks": ["string"],
  "recommended_next_step": "string",
  "follow_up_message_draft": "string"
}
```

### Agent 3 — `content_repurposer`
**Role:** content marketer / SMM repurposing layer.

**Input:** transcript + summary + brand voice.

**Output JSON:**
```json
{
  "telegram_post": "string",
  "instagram_caption": "string",
  "story_frames": [
    {
      "frame_no": 1,
      "text": "string"
    }
  ],
  "hooks": ["string"],
  "cta": "string",
  "sensitive_info_flags": ["string"]
}
```

---

## 11. Prompts for the 3 Subagents

### 11.1 System Prompt — `meeting_structurer`

```text
You are a meeting intelligence analyst.
Your job is to convert raw meeting transcripts and chat messages into a precise structured summary.

Rules:
1. Use only the information present in transcript/chat/metadata.
2. Do not invent facts, decisions, names, deadlines, or intentions.
3. If something is uncertain, reflect uncertainty explicitly.
4. Preserve the business meaning, not every filler phrase.
5. Extract concrete decisions, commitments, next steps, and open questions.
6. Include timestamps when they are available or derivable.
7. Output valid JSON only.
```

### 11.2 System Prompt — `sales_analyst`

```text
You are a B2B sales meeting analyst.
Your job is to analyze a meeting like a strong sales strategist.

Rules:
1. Separate observed facts from interpretation.
2. Infer the deal stage only from evidence.
3. Extract pains, goals, objections, buying signals, risks, and stakeholder roles.
4. Highlight missing information that blocks the sale.
5. Draft a practical follow-up message that sounds professional and human.
6. Do not exaggerate intent to buy.
7. Output valid JSON only.
```

### 11.3 System Prompt — `content_repurposer`

```text
You are a content strategist and social media repurposing assistant.
Your job is to turn a meeting transcript into useful public-facing content drafts.

Rules:
1. Keep only insights that are safe to publish.
2. Never expose confidential numbers, names, client secrets, or private agreements unless explicitly allowed.
3. Preserve the strongest insights, lessons, and hooks.
4. Adapt language for Telegram and Instagram.
5. Stories should be short, punchy, and sequential.
6. Output valid JSON only.
```

---

## 12. Guardrails

- всегда валидировать JSON после LLM
- если JSON сломан — запускать repair step
- если transcript слишком грязный — ставить `needs_review`
- если confidence низкий — помечать в output
- не публиковать контент автоматически без флага `safe_to_publish=true`
- для sales анализа не утверждать бюджет/сроки без прямого упоминания

---

## 13. Recommended n8n Workflow Design

### Workflow 1 — `meeting_webhook_ingest`
- Webhook (Fathom)
- Webhook (Zoom)
- Set / Code normalize
- Supabase upsert raw event
- Respond immediately

### Workflow 2 — `meeting_artifact_recovery`
- Schedule Trigger every 15 min
- Fetch meetings where status != processed
- HTTP Request to Fathom API / Zoom API
- Merge artifacts
- Update statuses

### Workflow 3 — `meeting_ai_pipeline`
- Trigger from DB / Execute Workflow
- Load meeting artifacts
- Preprocess transcript
- LLM: meeting_structurer
- JSON parse / repair
- LLM: sales_analyst
- JSON parse / repair
- LLM: content_repurposer
- JSON parse / repair
- Save outputs

### Workflow 4 — `meeting_delivery`
- Format Telegram message
- Send summary
- Send sales analysis
- Send content drafts
- Write delivery logs

### Workflow 5 — `meeting_monitoring`
- Schedule Trigger
- Check failed jobs
- Alert to Telegram admin channel
- Report webhook misses / retry counts

---

## 14. Fathom Webhook Debug Checklist

Если webhook перестал работать, проверить по порядку:

1. **Webhook URL не изменился?**
2. **Workflow active в n8n?**
3. **Используется production URL, а не test URL?**
4. **Fathom шлет на правильный endpoint path?**
5. **Не изменился HTTP method?**
6. **Нет ли 401 / 403 / 404 / 500 в execution logs?**
7. **Не сломалась signature verification / secret?**
8. **Не поменялся event name на стороне Fathom?**
9. **n8n отвечает слишком долго и Fathom timeout-ится?**
10. **Нет ли Cloudflare / reverse proxy / SSL проблем?**
11. **Webhook handler не делает тяжелую обработку до ответа?**
12. **Можно ли вручную воспроизвести запрос через curl/Postman?**

### Minimum debug strategy
- включить отдельный raw webhook logger
- логировать headers + body
- отвечать `200 OK` максимально быстро
- отдельно запускать downstream workflow
- сравнить старый и новый payload

---

## 15. Success Metrics

### Reliability
- webhook success rate
- % meetings recovered via fallback
- duplicate processing rate
- failed jobs rate

### Output quality
- summary usefulness score
- sales analysis accuracy score
- follow-up acceptance rate
- content publish rate

### Speed
- time from meeting end to summary delivered
- time from meeting end to sales analysis delivered
- time from meeting end to content draft delivered

---

## 16. Recommended Implementation Order

### Phase 1 — Reliability first
1. webhook ingestion
2. normalized schema
3. DB storage
4. fallback poller
5. status machine

### Phase 2 — AI outputs
6. meeting_structurer
7. sales_analyst
8. content_repurposer
9. JSON validation

### Phase 3 — Delivery and ops
10. Telegram delivery
11. alerting / monitoring
12. admin review mode
13. analytics dashboard

---

## 17. Best Practical Setup for Your Case

Для твоего кейса оптимальная схема такая:

- **Primary trigger:** Fathom webhook
- **Fallback trigger:** cron каждые 15 минут
- **Main orchestrator:** n8n
- **Storage:** Supabase
- **Outputs:** Telegram + n8n chat
- **AI pattern:** 1 canonical structurer + 2 specialized post-processors
- **Safety:** drafts first for content publishing

Это даст и надежность, и нормальную масштабируемость, если потом добавятся новые источники и каналы.

---

## 18. Reuse Strategy from Existing n8n Assets in This Repo

Я посмотрел существующие workflow-шаблоны в репо. Готового `Zoom/Fathom agent` JSON тут нет, но есть хорошие куски, которые можно переиспользовать почти без изобретения велосипеда.

### Что уже можно взять как паттерны

#### 1. `docs/summary_tg_chat.json`
Полезно как референс для:
- транскрибации аудио через Whisper HTTP
- длинной post-processing цепочки текста
- подготовки ответа для Telegram
- нормализации и chunking output

#### 2. `05_N8N_Automations/n8n_templates/WhatsApp_Summary_Agent_Evolution_API.json`
Полезно как референс для:
- простого webhook-first workflow
- fast response pattern
- media → transcribe → summarize → send back
- минимальной линейной архитектуры, которую легко адаптировать под Fathom

#### 3. `03_Marketing_and_Sales/b2b-lead-system/n8n-workflows/group_analyzer_workflow.json`
Полезно как референс для:
- schedule trigger / polling
- запись raw данных в Supabase
- idempotent-ish ingestion паттерна
- parsing JSON ответа LLM
- нормальной data-pipeline логики, а не просто one-shot summary

### Вывод

Самый правильный путь для твоего кейса:

- **не искать идеальный готовый Zoom/Fathom template**, которого тут нет,
- а **собрать новый workflow на коде в n8n**, используя уже готовые паттерны из этих 3 файлов.

---

## 19. Practical Fathom-First Implementation Plan

### Вариант, который я считаю лучшим

Сделать **2 workflow в n8n**, а не один гигантский:

### Workflow 1 — `fathom_webhook_ingest`
Минимальный и очень быстрый.

**Что делает:**
1. принимает webhook от Fathom
2. логирует весь `headers + body`
3. нормализует ключевые поля
4. пишет raw event в storage
5. быстро отвечает `200 OK`
6. отдельно создает задачу на downstream processing

**Почему так:**
- это лучший способ не терять webhook
- если AI/HTTP/supabase потом лагает, сам webhook все равно уже принят

### Workflow 2 — `meeting_processing_pipeline`
Асинхронный обработчик.

**Что делает:**
1. берет meeting/job из storage
2. проверяет, есть ли transcript / metadata / chat
3. если не хватает данных — помечает `awaiting_artifacts`
4. если данных хватает — запускает:
   - `meeting_structurer`
   - `sales_analyst`
   - `content_repurposer`
5. сохраняет outputs
6. шлет результат в Telegram / n8n chat

---

## 20. Minimum n8n Node Layout for Fathom Version

### Workflow 1 — `fathom_webhook_ingest`

**Nodes:**
1. `Webhook` — путь типа `/fathom-webhook`
2. `Code` — extract + normalize event
3. `HTTP Request / Supabase / Data Store` — save raw event
4. `IF` — event relevant?
5. `HTTP Request / Supabase / Data Store` — create processing job
6. `Respond to Webhook`

### Workflow 2 — `meeting_processing_pipeline`

**Trigger options:**
- `Schedule Trigger` every 2–5 min
- или `Execute Workflow` из ingest

**Nodes:**
1. load pending jobs
2. fetch meeting artifacts
3. optional HTTP request to Fathom API / Zoom API
4. `Code` normalize transcript/chat
5. LLM node: `meeting_structurer`
6. `Code` parse/repair JSON
7. LLM node: `sales_analyst`
8. `Code` parse/repair JSON
9. LLM node: `content_repurposer`
10. `Code` combine outputs
11. save final result
12. Telegram send

---

## 21. What to Check in n8n Right Now

Если хочешь проверить уже сейчас руками, без полной сборки, вот что смотреть в n8n:

1. есть ли вообще workflow с Fathom webhook path
2. активен ли он (`Active = true`)
3. production ли webhook URL используется в Fathom
4. появляется ли execution при ручном тестовом запросе
5. есть ли `Respond to Webhook` / быстрый ответ
6. нет ли тяжелого AI before response
7. есть ли логирование raw body

Если этого нет, значит проблема не в агенте, а уже в самом ingest слое.

---

## 22. Recommended Build Order from Here

### Step 1
Сначала собрать **только Fathom ingest workflow** и убедиться, что webhook стабильно ловится.

### Step 2
Потом подключить **один агент** — `meeting_structurer`.

### Step 3
Потом расширить до `sales_analyst` и `content_repurposer`.

### Step 4
Добавить Telegram delivery.

### Step 5
Добавить fallback cron/poller.

Это правильнее, чем сразу собирать весь монолит.

---

## 23. Telegram-First MVP Scope

Ок, как промежуточный первый этап делаем **Telegram bot intake/output**, но так, чтобы потом без боли подключить Fathom webhook в ту же архитектуру.

### MVP Goal

Сделать Telegram-бота, который принимает:
- обычный текст
- Telegram voice
- audio file
- `.m4a`
- iPhone Voice Memo
- опционально video / video note

И возвращает в Telegram:
1. summary
2. sales analysis
3. content drafts

---

## 24. Supported Telegram Inputs for v1

### Must-have
- `message.text`
- `message.voice`
- `message.audio`
- `message.document` with extensions:
  - `.m4a`
  - `.mp3`
  - `.wav`
  - `.aac`
  - `.ogg`

### Nice-to-have in v1 or v1.1
- `message.video_note`
- `message.video`

### Detection Rules

Нужно принимать файл не только по mime type, но и по комбинации:
- telegram field type
- mime type
- file extension
- file name

Потому что iPhone voice memo и пересланные файлы часто приходят не идеально консистентно.

---

## 25. Telegram Intake Workflow

### Workflow — `tg_meeting_assistant_ingest`

**Nodes:**
1. `Telegram Trigger`
2. `Code` — detect input type
3. `Switch / IF`
   - text
   - voice
   - audio
   - document
   - video/video_note
4. `Telegram Get File`
5. `HTTP Request` download binary
6. `Code` normalize media metadata
7. `Whisper / STT`
8. `Code` build canonical input
9. `meeting_structurer`
10. `sales_analyst`
11. `content_repurposer`
12. `Telegram Send Message`

---

## 26. Canonical Input for Telegram Sources

```json
{
  "source": "telegram_text|telegram_voice|telegram_audio|telegram_document|telegram_video",
  "chat_id": "string",
  "user_id": "string",
  "message_id": "string",
  "file_id": "string|null",
  "mime_type": "string|null",
  "file_name": "string|null",
  "file_ext": "string|null",
  "text": "string|null",
  "transcript_text": "string|null",
  "language": "ru",
  "received_at": "2026-04-15T10:00:00Z",
  "metadata": {}
}
```

---

## 27. Media Handling Rules

### Text
- идет напрямую в pipeline

### Voice / Audio / M4A / Voice Memo
- скачиваем файл
- если STT понимает формат напрямую — отправляем как есть
- если нет — конвертируем в совместимый формат
- получаем transcript
- дальше стандартный pipeline

### Video / Video Note
- для MVP можно делать так:
  - извлечь аудио дорожку
  - отдать в STT
  - дальше стандартный pipeline

Если extraction на старте слишком усложняет MVP, можно временно:
- поддержать только те видео, где сервис транскрибации сам умеет извлекать аудио
- иначе отвечать сообщением `video format not yet supported fully`

---

## 28. Recommended MVP Priorities

### v1
- text
- voice
- audio
- m4a
- iPhone voice memo

### v1.1
- video note
- video

### v2
- Fathom webhook
- Zoom webhook
- fallback poller
- meeting storage + dashboard

---

## 29. Practical Recommendation

Самый быстрый и правильный путь сейчас такой:

1. собрать `tg_meeting_assistant_ingest`
2. убедиться, что бот стабильно принимает:
   - текст
   - войс
   - m4a
   - voice memo с iPhone
3. подключить 3 агентов
4. потом добавить video/video note
5. потом уже подключить Fathom webhook в тот же processing layer

То есть Telegram MVP не отменяет Fathom, а просто дает быстрый и удобный intake-контур для отладки всей логики.