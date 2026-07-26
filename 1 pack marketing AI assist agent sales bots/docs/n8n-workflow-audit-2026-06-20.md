# N8N Workflow Audit — 2026-06-20

## Scope
- Директория: `05_N8N_Automations/workflows/prod/`
- Проверены: 4 файла

## Исправленные проблемы

### 1. Test_Fallback.workflow.ts
- **Проблема:** невалидный параметр `ai_fallbackModel` (не поддерживается текущим трансформером)
- **Исправление:** заменён на явный fallback Agent через `onError → out(1)`
- **Дополнительно:** добавлен `id` в `@workflow({...})`, добавлен `projectId`

### 2. Google_Assistant_Low_Cost_Fallback.workflow.ts
- **Проблема:** опечатка в параметре Memory — `contextWindowLength` вместо `contextWindowLength`
- **Исправление:** исправлено на `contextWindowLength: 10`

### 3. AI_Agent_Multi_Provider.workflow.ts
- **Проблема:** отсутствовал `id` в `@workflow({...})` и `projectId`
- **Исправление:** добавлены оба поля

## Подтверждённые runtime-проблемы (live execution feedback)

### 00 - ГЛАВНЫЙ + GOOGLE Ассистент ЛИЧНЫЙ Pod
- **Error 1:** `Analyze image` → `Forbidden - perhaps check your credentials?`
  - Вероятная причина: невалидный/просроченный Gemini API key в credential `07mn330Ii1yGriyp`
  - Действие: обновить credential в n8n UI или заменить на актуальный ключ
- **Error 2:** `HTTP Request2 GOOGLE CAL` → `Bad request - please check your parameters`
  - Вероятная причина: неверный endpoint/params в HTTP Request ноде к Google Calendar
  - Действие: проверить URL, headers, body в соответствующей ноде

## Подтверждённые runtime-проблемы (live execution feedback)

### 00 - ГЛАВНЫЙ + GOOGLE Ассистент ЛИЧНЫЙ Pod
- **Error 1:** `Analyze image` → `Forbidden - perhaps check your credentials?`
  - Вероятная причина: невалидный/просроченный Gemini API key в credential `07mn330Ii1yGriyp`
  - Действие: обновить credential в n8n UI или заменить на актуальный ключ
- **Error 2:** `HTTP Request2 g cal goole` → `Bad request - please check your parameters` (400)
  - Вероятная причина: неверный путь в URL вызова Google Calendar через Maton.
  - В логе нода:
    - URL: `https://api.maton.ai/google-calendar/calendar/v3/calendars/primary/events`
    - Ошибка Maton о том, что URL path MUST начинаться с `/google-calendar/...`
  - Скорее всего, правильный формат: `https://api.maton.ai/google-calendar/v3/calendars/primary/events` (без двойного `calendar`).
  - Действие: поправить URL в ноде на `.../google-calendar/v3/...` или перейти на нативную `Google Calendar` ноду.

## Оставшиеся риски
- Главный workflow содержит хардкод API-ключей в нодах (Google TTS, Suno/KIE, и др.)
- Устаревшие/несуществующие model ID (например `models/gemini-3-flash-preview`, `models/gemini-3.1-flash-lite-preview-09-2025`, `models/nano-banana-pro-preview`)
- Дубликаты node property names в одном файле могут нарушать push

## Рекомендации
1. Приоритет: исправить credentials для `Analyze image` (Gemini) — без этого падает whole pipeline обработки фото
2. **Google Calendar (требует recurring events):**
   - Сейчас запрос падает с 400 из-за неверного URL path и/или формата body.
   - Вариант A: Перейти на нативную Google Calendar ноду — она корректно поддерживает `recurrence` (RRULE) и избавляет от двойного mapping через Maton.
   - Вариант B: Оставить через Maton, но поправить URL на `.../google-calendar/v3/...` и расширить body полем `recurrence` (например `RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR`).
3. Вынести все API-ключи из кода в n8n credentials/environment variables
4. Обновить model ID на актуальные из доступных в аккаунте
5. Сделать отдельный аудит дубликатов имён нод в главном workflow
