# Outreach MVP Blueprint

## Что это

Минимальный внутренний MVP для WhatsApp outreach на текущем стеке:

- `Evolution API` — транспорт и сессии WhatsApp
- `n8n` — оркестрация отправок и webhook-обработки
- `Supabase/Postgres` — source of truth по лидам, сообщениям, ответам и blocklist
- `Hermes` — операторский слой в Telegram при необходимости

Цель — не строить сразу SaaS, а быстро получить рабочую систему для себя:

- отправка по одному;
- логирование каждой отправки;
- статусы `sent/delivered/read/replied/failed`;
- reply tracking;
- STOP / blacklist;
- кампании, теги и сегменты.

---

## MVP-сущности

### 1. `campaigns`

Нужна для группировки отправок по офферу, базе или гипотезе.

Основные поля:

- `name`
- `source`
- `segment`
- `offer_angle`
- `status`

### 2. `leads`

Главная карточка контакта.

Основные поля:

- `phone`
- `name`
- `company_name`
- `source`
- `niche`
- `website`
- `instagram`
- `whatsapp_name`
- `whatsapp_business_title`
- `whatsapp_business_description`
- `pain_hypothesis`
- `offer_angle`
- `personal_hook`
- `generated_pitch`
- `tags`
- `ai_score`
- `status`

### 3. `messages`

Каждая отправка или входящее сообщение = отдельная запись.

Основные поля:

- `lead_id`
- `campaign_id`
- `direction`
- `instance_name`
- `sender_number`
- `recipient_phone`
- `content`
- `wa_message_id`
- `provider_status`
- `sent_at`
- `delivered_at`
- `read_at`
- `replied_at`
- `failed_at`

### 4. `message_status_events`

Подробная лента событий по webhook/runtime.

Примеры событий:

- `outbound_accepted`
- `message_sent`
- `message_delivered`
- `message_read`
- `message_failed`
- `incoming_reply`
- `stop_detected`

### 5. `replies`

Нормализованное хранилище ответов клиента.

Поля:

- `reply_text`
- `reply_type`
- `reply_at`

### 6. `blocklist`

Список телефонов, которым нельзя писать.

Причины:

- `stop_requested`
- `manual_block`
- `invalid_number`
- `replied_negative`
- `duplicate_contact`

---

## Статусы лида

Рекомендуемые lead statuses:

- `new`
- `enriched`
- `queued`
- `sent`
- `delivered`
- `read`
- `replied`
- `interested`
- `not_interested`
- `followup_due`
- `blacklisted`
- `invalid_number`
- `closed`

---

## Статусы сообщений

Рекомендуемые message statuses:

- `queued`
- `pending`
- `sent`
- `delivered`
- `read`
- `replied`
- `failed`
- `blocked`

---

## Карта workflow в n8n

### Workflow A — `outreach_send_single`

Назначение: отправка по одному контакту.

Шаги:

1. Получить лид из `leads` со статусом `queued`.
2. Проверить `blocklist`.
3. Проверить cooldown / не отправляли ли уже недавно.
4. Выбрать `instance_name`.
5. Отправить в Evolution API.
6. Сохранить запись в `messages`.
7. Сохранить событие в `message_status_events`.
8. Обновить lead status на `sent` или `invalid_number/failed`.

### Workflow B — `evolution_webhook_ingest`

Назначение: принимать входящие webhook-события от Evolution.

Обрабатывать:

- `messages.upsert`
- `messages.update`
- `message.sent`
- `session.status`

Шаги:

1. Принять webhook.
2. Быстро вернуть `200 OK`.
3. Нормализовать payload.
4. Найти `lead` и/или `message`.
5. Записать событие в `message_status_events`.
6. Обновить `messages.provider_status`.
7. Если это входящий ответ — создать запись в `replies`.
8. Обновить `leads.status`.

### Workflow C — `stop_blacklist_handler`

Назначение: STOP / отписка / негатив.

Правила:

- если текст содержит `стоп`
- или `stop`
- или `не пишите`
- или `не интересно`

Действия:

1. Добавить номер в `blocklist`.
2. Обновить `leads.status = blacklisted`.
3. Записать `message_status_events` с типом `stop_detected`.

### Workflow D — `followup_scheduler`

Назначение: планировать follow-up.

Стартовый MVP-вариант:

- day 0 — первое касание
- day 1 — follow-up 1
- day 3 — follow-up 2

Follow-up отправлять только если:

- нет ответа;
- номер не в `blocklist`;
- последнее сообщение не `failed`.

---

## Политика по номерам

Текущий operational baseline:

- основной номер: `8326 301 n8n wa 1`
- fallback номер: `35 20` после стабилизации / открытия
- старый резерв: `4877` после повторного логина

MVP-правило:

- сначала работаем с одним основным номером;
- fallback включаем только после стабилизации tracking layer;
- не отправлять сразу большими пачками.

---

## Что запускать первым

### Этап 1

Накатить SQL из `06_Scripts_and_Tools/init_supabase.sql`.

### Этап 2

Собрать два workflow:

- `outreach_send_single`
- `evolution_webhook_ingest`

Стартовые JSON-заготовки уже добавлены в проект:

- `n8n_templates/outreach_send_single_mvp.json`
- `n8n_templates/evolution_webhook_tracking_mvp.json`

### Этап 3

Добавить логику STOP / blacklist.

### Этап 4

Сделать smoke test:

- 1 номер
- 1 отправка
- 1 статусный webhook
- 1 reply webhook

### Этап 5

Пилот на 3–10 контактов.

---

## Что не делаем в этом MVP

Пока не делаем:

- полноценный web dashboard;
- multi-tenant SaaS;
- billing;
- сложные роли и права;
- account farm / массовую автоматическую регистрацию;
- full AI autopilot sales agent.

Сначала нужен рабочий operational core.

---

## Следующий практический шаг

После наката SQL:

1. собрать `outreach_send_single.json`;
2. собрать `evolution_webhook_ingest.json`;
3. протестировать на одном реальном контакте;
4. проверить, что в БД заполняются:
   - `messages`
   - `message_status_events`
   - `replies`
   - `blocklist`.

### Что заменить перед импортом в n8n

В обоих workflow замени значения-заглушки:

- `REPLACE_SUPABASE_URL`
- `REPLACE_SUPABASE_SERVICE_ROLE_KEY`
- `REPLACE_EVOLUTION_API_KEY`
- `REPLACE_EVOLUTION_INSTANCE` — если нужен другой основной instance