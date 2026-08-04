# 📓 Дневник разработки — ИИ с руками / Контент Завод
_Последнее обновление: 2026-08-04_

---

## ✅ Что сделано и работает

### Telegram-бот (`/api/bot/route.ts`)
- [x] Вебхук принимает сообщения и инлайн-кнопки
- [x] `/start` — приветствие с главным меню (инлайн-кнопки)
- [x] `/ref` и callback `referral` — реф-ссылка пользователя
- [x] `callback: profile` — показывает профиль и баланс токенов
- [x] Реферальная система: `/start ref_<id>` → +50 токенов пригласившему
- [x] Логи в Supabase (таблица `logs`)
- [x] Логи администратора в Telegram-канал через `sendAdminNotification`
- [x] **Отключены спам-логи для ADMIN_ID (888005446)** — ваши действия больше не дублируются
- [x] `/connect` и кнопка «Подключить сервисы» — меню Nango интеграций
- [x] **State Machine** для пошаговой генерации каруселей:
  - `/carousel` → переводит в `wait_topic`
  - Пользователь пишет тему → бот делает черновик
  - Кнопки: `✅ Утвердить / 🔄 Изменить / ❌ Отмена`

### API (`/api/draft-carousel/route.ts`)
- [x] Gemini API через `GEMINI_API_KEY` (фолбэк)
- [x] Vertex AI через `GOOGLE_APPLICATION_CREDENTIALS_JSON` (приоритет)
- [x] **Убраны спам-логи** генерации в Telegram-канал
- [x] Возвращает структурированный JSON: `[{title, subtitle, body, imagePrompt}]`

### Mini App (Next.js на Vercel)
- [x] `/dashboard` — главная страница с карточками функций
- [x] `/dashboard/carousel-generator` — полная страница генерации каруселей:
  - Загрузка референс-изображения
  - Чат-режим доработки черновика
  - Генерация финальных картинок (Vertex AI / HTML-to-image)
  - Скачивание ZIP-архива слайдов
- [x] `/dashboard/integrations` — **новая страница** интеграций с Google/Notion (Nango OAuth ссылки)
- [x] Auth через Telegram WebApp (`initDataUnsafe.user`)

### Supabase
- [x] Таблица `users` — telegram_id, username, tokens, referred_by
- [x] Таблица `logs` — история действий
- [x] Функция `increment_tokens` — начисление токенов
- [x] **Новые колонки** `state` и `state_data` для State Machine (миграция `00002`)
- [x] Спроектирована постоянная память ассистента, контекст документов и task routing (гайд `docs/ASSISTANT_MEMORY_AND_TASKS.md`)
- [x] Добавлена миграция `00003_assistant_memory_tasks.sql` для `assistant_profiles`, `assistant_memories`, `conversation_messages`, `knowledge_sources`, `knowledge_chunks`, `agent_tasks`, `agent_task_events`
- [x] RLS отключён (управление только через server-side API)

### Nango SDK
- [x] `@nangohq/node` установлен в проект
- [x] Ссылки авторизации формируются динамически (per user)
- [ ] **Сам Nango-сервер НЕ задеплоен** — нужен VPS с Docker

---

## 🚨 КРИТИЧЕСКИЕ задачи (нужно сделать СЕЙЧАС)

### 1. Добавить переменные в Vercel
Зайти в https://vercel.com → ваш проект → Settings → Environment Variables:

| Переменная | Значение |
|---|---|
| `GEMINI_API_KEY` | ключ от AI Studio (makersuite.google.com) |
| `NANGO_SECRET_KEY` | Secret key из Nango Dashboard |
| `NEXT_PUBLIC_NANGO_PUBLIC_KEY` | Public key из Nango Dashboard |

### 2. Применить миграцию в Supabase
Зайти в https://supabase.com → ваш проект → SQL Editor:
```sql
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS state TEXT DEFAULT 'idle';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS state_data JSONB;
```

### 3. Задеплоить Nango на VPS
Без этого кнопки подключения Google/Notion будут вести в никуда.
Нужен VPS с Docker и открытыми портами 80/443.

---

## 🔲 TODO (следующий спринт)

### Бот
- [ ] Показывать баланс токенов при каждой генерации
- [ ] Команда `/status` — статус подключённых интеграций (Google, Notion)
- [ ] Дедукция 1 токена при каждой генерации черновика
- [ ] Сохранять входящие/исходящие сообщения в `conversation_messages`
- [ ] Вычислять `session_key` для DM, group chat и forum topic (`message_thread_id`)
- [ ] Перед LLM-вызовом подмешивать профильную память, последние сообщения и релевантные knowledge chunks
- [ ] Нормализовать execution-запросы в `agent_tasks` перед выполнением

### Mini App
- [ ] Страница `/dashboard/integrations` — показывать статус "подключено/нет"
- [ ] Страница `/dashboard/billing` — пополнение токенов
- [ ] Страница `/dashboard/calendar` — просмотр Google Calendar через Nango proxy
- [ ] Admin/debug view для memories, knowledge sources и agent tasks

### Nango / OAuth
- [ ] Задеплоить Nango на VPS (Docker, HTTPS)
- [ ] Настроить Google OAuth Credentials (Client ID + Secret) в Google Cloud Console
- [ ] Настроить Notion OAuth app
- [ ] Реализовать `/api/ai-agent/route.ts` с `nango.proxy` для реальных запросов к Google API

---

## 📊 Архитектура проекта

```
Telegram Bot
    ↓ Webhook
Vercel Edge Functions (/api/bot)
    ↓ upsert/select
Supabase PostgreSQL
    ↓ (токены, users, logs, state)

Vercel (/api/draft-carousel)
    ↓ generateContent
Vertex AI / Gemini API
    ↓ слайды JSON
Bot → User (черновик + кнопки)

Mini App (Next.js / Vercel)
    /dashboard — главная
    /dashboard/carousel-generator — генерация
    /dashboard/integrations — OAuth подключение (→ Nango)
    ↓ OAuth flow
Nango Server (VPS, Docker) [НЕ ЗАДЕПЛОЕН]
    ↓ токены пользователей
Google Calendar / Docs / Notion API
```

---

## 🔑 Критические переменные окружения

| Переменная | Где нужна | Статус |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Vercel | ✅ Есть |
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel | ✅ Есть |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel | ✅ Есть |
| `SUPABASE_SERVICE_ROLE_KEY` | Vercel | ✅ Есть |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Vercel | ✅ Есть (SA JSON) |
| `GEMINI_API_KEY` | Vercel | ❌ НЕ ДОБАВЛЕН |
| `NANGO_SECRET_KEY` | Vercel | ❌ НЕ ДОБАВЛЕН |
| `NEXT_PUBLIC_NANGO_PUBLIC_KEY` | Vercel | ❌ НЕ ДОБАВЛЕН |
| `ADMIN_CHAT_ID` | Vercel | ✅ 888005446 захардкожен в коде |

---
_Автор: AI с руками (Antigravity). Версия: 2.0_
