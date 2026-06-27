# N8 Assistant v2 — Гайд для AI-агентов

Этот проект — многоагентная разработка. Пожалуйста, соблюдай следующие правила.

## Как работать

### 1. Ознакомься с проектом

Всегда начинай с чтения:
- `docs/ARCHITECTURE.md` — общая архитектура
- `docs/SPECIFICATION.md` — спецификация фич
- `docs/AGENTS_GUIDE.md` — этот файл

### 2. Принципы

- **TypeScript строго** — никаких `any`, `as`, `@ts-ignore`
- **Next.js App Router** — Server Components, Server Actions
- **Supabase** — все данные через клиент Supabase
- **grammy** — Telegram Bot фреймворк
- **Tailwind CSS v4** — стилизация
- **ESLint** — перед коммитом

### 3. Структура для нового кода

```
src/bot/           # Telegram Bot
  ├── index.ts     # Точка входа (webhook)
  ├── handlers/    # Обработчики update-ов
  ├── services/    # Бизнес-логика (внешние API)
  └── utils/       # Хелперы

src/app/           # Next.js App Router (веб + Mini App)
  ├── api/         # API route handlers
  │   └── bot/     # Webhook endpoint
  └── (routes)     # Страницы

src/utils/         # Общие утилиты
  └── supabase/    # Supabase клиенты
```

### 4. Telegram Bot — конвенции

- Используй `grammy` (не telegraf, не node-telegram-bot-api)
- Webhook, не long polling (для Vercel)
- Все обработчики в отдельных файлах в `handlers/`
- Все вызовы внешних API в `services/`
- Ошибки логировать, но не ронять бота

### 5. Multi-LLM Router — конвенции

- Все провайдеры реализуют единый интерфейс `LLMProvider`
- Логирование каждого запроса в `llm_usage_logs`
- Провайдеры в порядке приоритета: OpenRouter → Google → Groq → AIHubMix → Vertex

### 6. Supabase — конвенции

- Таблицы всегда с `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- Всегда ставить `created_at TIMESTAMPTZ DEFAULT NOW()`
- RLS включено на всех таблицах
- Миграции через Supabase CLI

### 7. Telegram Mini App

- Поддержка `window.Telegram.WebApp` API
- Адаптивный дизайн под Mini App (ширина 100%, высота auto)
- Init data валидация через HMAC

### 8. Git

- Ветка: `main` (пока один разработчик)
- Коммиты: семантические (`feat:`, `fix:`, `docs:`, `chore:`)
- ESLint перед каждым коммитом

### 9. Переменные окружения (.env.local)

```
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=

# AI Providers
OPENROUTER_API_KEY=
GOOGLE_AI_STUDIO_API_KEY=
GROQ_API_KEY=
AIHUBMIX_API_KEY=

# Social Media
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=

# YouTube
YOUTUBE_API_KEY=

# Storage
SUPABASE_STORAGE_BUCKET=media
```
