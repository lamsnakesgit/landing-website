# N8 Assistant v2 — Архитектура

> **Версия:** 2.0  
> **Статус:** В разработке (MVP)  
> **Фреймворк:** Next.js 16 + React 19 + TypeScript  
> **База данных:** Supabase (Postgres)  
> **Бот:** Telegram Bot (grammy) + Telegram Mini App  

---

## 1. Общая архитектура

```
TELEGRAM (основной интерфейс)
  ├── Telegram Bot (@n8assistant_bot)
  │   • Голосовые / аудио / транскрипция
  │   • Фото анализ / генерация
  │   • Команды / рефералка
  │   • Карусели
  └── Telegram Mini App (Next.js внутри TG)
      • Дашборд / настройки
      • Подключение соцсетей
      • Аналитика / история
      • Кредиты / биллинг
          │
     Webhook │ Mini App Init
          ▼
BACKEND (Next.js API + Serverless)
  ├── Auth (Supabase — email / telegram_id)
  ├── AI Router (Multi-LLM: OpenRouter → Google → Groq → AIHubMix)
  ├── Social Scheduler (Cron + Queue → FB / IG / Threads APIs)
  └── Media Processor (Whisper / Gemini Vision / ffmpeg)
          │
          ▼
SUPABASE (Postgres)
  • users | referrals | llm_logs
  • social_accounts | scheduled_posts | analytics
  • transactions | media_cache | carousels
```

---

## 2. Структура проекта

```
n8-assistant-v2/
├── public/carousels/       # HTML-карусели для Instagram
├── docs/                   # Документация
│   ├── ARCHITECTURE.md     # Этот файл
│   ├── SPECIFICATION.md    # Полная спецификация
│   ├── AGENTS_GUIDE.md     # Гайд для AI-агентов
│   ├── dev_diary.md        # Дневник разработки
│   └── marketing_strategy.md
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── page.tsx        # Лендинг
│   │   ├── layout.tsx      # Root layout
│   │   ├── globals.css     # Tailwind CSS
│   │   ├── login/          # Auth страница
│   │   └── dashboard/      # Дашборд (защищённый)
│   ├── bot/                # Telegram Bot (grammy)
│   │   ├── index.ts        # Entry point / webhook handler
│   │   ├── handlers/       # Обработчики
│   │   │   ├── start.ts
│   │   │   ├── voice.ts    # Голосовые
│   │   │   ├── photo.ts    # Фото
│   │   │   ├── audio.ts    # Аудио
│   │   │   ├── text.ts     # Текст
│   │   │   └── refer.ts    # Рефералка
│   │   ├── services/
│   │   │   ├── transcription.ts  # Whisper / Deepgram
│   │   │   ├── image.ts          # Анализ / генерация
│   │   │   ├── youtube.ts        # YouTube
│   │   │   ├── carousel.ts       # Карусели
│   │   │   └── llm.ts            # Multi-LLM router
│   │   └── utils/
│   ├── middleware.ts       # Supabase middleware
│   └── utils/supabase/     # Supabase клиенты
├── package.json
├── tsconfig.json
└── .env.local
```

---

## 3. Аутентификация

### Supabase Auth (email + пароль) — для веб-входа
### Telegram Auth — при /start создаётся юзер по telegram_id
### Mini App — валидация через HMAC (telegramWebAppData)

```sql
CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id UUID REFERENCES auth.users(id),
  telegram_id BIGINT UNIQUE,
  telegram_username TEXT,
  email TEXT UNIQUE,
  phone TEXT,
  display_name TEXT,
  avatar_url TEXT,
  credits_balance NUMERIC DEFAULT 0,
  role TEXT DEFAULT 'user',
  system_prompt TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active_at TIMESTAMPTZ
);
```

---

## 4. Multi-LLM Router

**Приоритет:** OpenRouter → Google AI Studio (Gemini Flash) → Groq → AIHubMix → Vertex AI

```sql
CREATE TABLE llm_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  provider TEXT,
  model TEXT,
  input_tokens INT,
  output_tokens INT,
  cost_usd NUMERIC,
  duration_ms INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. Voice / Audio Pipeline

```
Telegram Voice (.ogg) → Download → Convert to MP3 (ffmpeg)
  → Whisper API / Deepgram → Транскрипт → AI обработка → Ответ
```

Поддерживается: Telegram Voice, MP3, WAV, M4A, OGG, видео (извлекается аудио)

---

## 6. Image Pipeline

- **OCR / чтение текста:** Photo → Gemini Flash Vision → текст
- **Deep Analysis:** Photo + Prompt → Gemini Flash Vision → анализ
- **Генерация:** Prompt → OpenRouter (Flux / Recraft / SD) → Image URL

---

## 7. Social Scheduler

**Платформы:** Facebook (Graph API), Instagram (Graph API), Threads (Threads API)

```sql
CREATE TABLE scheduled_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  platform TEXT,
  content JSONB,
  scheduled_at TIMESTAMPTZ,
  status TEXT DEFAULT 'pending',
  published_at TIMESTAMPTZ,
  media_urls TEXT[],
  thread_parent_id UUID,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 8. Реферальная система (3 уровня)

```sql
CREATE TABLE referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id UUID REFERENCES users(id),
  referred_id UUID REFERENCES users(id),
  level INT CHECK (level BETWEEN 1 AND 3),
  bonus_credits NUMERIC DEFAULT 0,
  commission_rate NUMERIC DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE referral_earnings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  from_user_id UUID REFERENCES users(id),
  amount NUMERIC,
  type TEXT,
  level INT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Схема:** L1: +20%/10% | L2: +10%/5% | L3: +5%/2.5% | Мин. вывод: 1000 CR

---

## 9. YouTube + Google Drive

- **Анализ:** ссылка → ytdl-core → транскрипция → сводка
- **Загрузка:** YouTube Data API v3 + Google Drive API + ffmpeg

---

## 10. Deploy

**Current Deployment:** MVP stage deployed to Vercel.
- **Production URL:** `https://n8-assistant-v2.vercel.app`
- **Environment Variables:** `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are configured via Vercel CLI.

| Stage | Cost | Users |
|---|---|---|
| MVP (Vercel Free + Supabase Free) | $0 | ~200 |
| Growth (Vercel Pro $20 + Supabase Pro $25) | $45 | ~2000 |
| Scale (VPS $20 + Supabase Team $599) | $620 | 10K+ |
