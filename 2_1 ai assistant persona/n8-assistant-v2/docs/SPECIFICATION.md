# N8 Assistant v2 — Спецификация

## 1. Telegram Bot

### 1.1 Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие + регистрация |
| `/ref` | Реферальная ссылка + статистика |
| `/credits` | Баланс кредитов |
| `/settings` | Настройки (системный промпт, язык) |
| `/help` | Справка |

### 1.2 Обработка медиа

- **Голосовые (voice):** Скачать OGG → конверт в MP3 → Whisper API → транскрипт → ответ
- **Аудио (mp3, wav, etc.):** Скачать → Whisper API → транскрипт → ответ
- **Фото:** Скачать → Gemini Flash Vision (OCR или анализ по контексту) → ответ
- **Видео:** Скачать → ffmpeg извлечь аудио → Whisper API → транскрипт → ответ
- **YouTube ссылка:** ytdl-core → аудио → транскрипт → сводка

### 1.3 Карусели

- Команда `/carousel` или кнопка в Mini App
- AI генерирует HTML-карусель (1080×1350, Instagram 4:5)
- Сохраняется в `public/carousels/`
- Предлагает доработать промпт

### 1.4 Рефералка

- Генерация ссылки `https://t.me/n8assistant_bot?start=ref_{user_id}`
- 3 уровня: L1=20%, L2=10%, L3=5%
- Бонус за регистрацию: +50 CR рефералу, +20% CR рефереру
- Процент с покупок: L1=10%, L2=5%, L3=2.5%
- Мин. вывод: 1000 CR

## 2. Telegram Mini App

- Открывается через кнопку "Открыть панель" в боте
- Ссылка: `https://n8-assistant.vercel.app` (или кастом домен)
- Next.js адаптируется под Telegram WebApp API
- Vercel Deploy

## 3. Multi-LLM Router

### Провайдеры (в порядке приоритета):

1. **OpenRouter** — единый API, fallback, метрики. OpenAI-совместимый
2. **Google AI Studio** — Gemini Flash (free: 60 req/min)
3. **Groq** — Llama/Mixtral (free: 30 req/min)
4. **AIHubMix** — китайские модели, дёшево
5. **Vertex AI** — Google Cloud, для production

### Логирование:
- Все запросы пишутся в `llm_usage_logs`
- Дашборд "Потребление AI" по провайдерам, моделям, юзерам

## 4. Социальный Scheduling

### Поддерживаемые платформы

**Facebook:**
- Facebook Graph API v22.0
- Типы: текст, фото, видео, карусель
- Требуется: Facebook Page + Access Token

**Instagram:**
- Instagram Graph API
- Только Business/Creator аккаунты
- Типы: Image, Video, Carousel, Reels
- Метод: create container → publish

**Threads:**
- Threads API (`graph.threads.net`)
- Типы: TEXT, IMAGE, VIDEO, CAROUSEL
- Reply chains: создание цепочки постов (треды)
- Бесплатно, rate-limit по impressions

### Scheduling Engine
- Таблица `scheduled_posts` в Supabase
- Vercel Cron (каждую минуту проверять)
- Выбор платформы при создании поста
- Статусы: pending → publishing → published / failed

## 5. Аналитика

### Account Analytics
- followers, following, reach, impressions, profile_views
- Обновление: раз в день (cron)

### Post Analytics
- likes, comments, shares, saves, reach, impressions
- По каждому опубликованному посту

## 6. YouTube Integration

- Получение ссылки на видео
- ytdl-core: извлечение аудиодорожки
- Whisper API: транскрипция всего видео
- AI: саммари, ключевые моменты
- Опционально: загрузка на свой канал (YouTube Data API v3)
- Опционально: загрузка на Google Drive

## 7. Image Generation

- Prompt → OpenRouter (Stability AI / Flux Pro / Recraft) → Image URL
- Сохранение в Supabase Storage
- Отправка в Telegram

## 8. Per-User Memory

- `users.system_prompt` — кастомный системный промпт для каждого юзера
- Сохраняется история диалогов (Supabase)
- Контекст: последние N сообщений
- Постоянная память и task routing описаны в `docs/ASSISTANT_MEMORY_AND_TASKS.md`.
- Для Telegram group/forum topic память должна быть scoped по `chat_id` + `message_thread_id`, чтобы разные топики не смешивались.
- Execution-запросы должны нормализоваться в `agent_tasks` перед выполнением: route, objective, priority, status, context.

## 9. Бонус: Carousel Generation

- AI генерирует HTML-карусель по теме
- Viral storytelling структура (hook → problem → reframe → mechanism → proof → action → CTA)
- Watermark: @lamanopro_ × @aiconicvibe
- Размер: 1080×1350 (Instagram 4:5)
- Предлагает доработать промпт
- Export в PNG
