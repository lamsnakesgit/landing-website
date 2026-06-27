# Дневник Разработки (Dev Diary)

## [2026-06-27] Архитектура + Telegram Bot + Документация для multi-agent
**Wins:**
- Создана полная архитектура (ARCHITECTURE.md)
- Написана спецификация (SPECIFICATION.md) — все фичи расписаны
- Создан AGENTS_GUIDE.md — гайд для параллельной работы AI-агентов
- Установлен grammy (Telegram Bot framework)
- Создан Telegram Bot каркас:
  - `/start` — регистрация через telegram_id
  - `/ref` — 3-уровневая рефералка
  - `/help`, `/credits`, `/settings`
  - Голосовые → Whisper API → транскрипт
  - Аудиофайлы → Whisper API → транскрипт
  - Фото → Gemini Flash Vision → анализ
  - Текст → Multi-LLM Router (OpenRouter → Google AI Studio)
  - Webhook endpoint (`POST /api/bot`)
- Multi-LLM Router с fallback: OpenRouter → Google Gemini Flash
- Whisper API + Deepgram fallback для транскрипции
- Обновлён .env.local со всеми переменными
- TypeScript компилируется без ошибок

**Next Steps:**
- Запустить бота (нужен TELEGRAM_BOT_TOKEN и WEBHOOK_URL)
- Подключить Google AI Studio API (фото анализ)
- Добавить YouTube анализ
- Добавить генерацию каруселей в HTML
- Создать Supabase таблицы (users, referrals, llm_logs)

---

## [2026-06-22] Инициализация проекта и Фаза 1
**Wins (Победы):**
- Успешно инициализировали Next.js (App Router, Tailwind, TypeScript).
- Создали главную страницу (Лендинг) с современным Glassmorphism дизайном.
- Создали структуру Личного кабинета (Дашборд) с отображением кредитов.
- Интегрировали Supabase (Auth, RLS, Триггеры для выдачи кредитов).
- Написали Middleware для защиты приватных роутов.
- Сформулировали крутое маркетинговое позиционирование ("ИИ с руками").

**Problems / Issues (Проблемы и решения):**
- *Проблема:* Упал редирект после логина (ошибка `x-action-redirect` из-за кириллицы в Next.js 14+).
- *Решение:* Обернули текст ошибки в `encodeURIComponent()`.
- *Проблема:* Ошибка сборки `No space left on device (os error 28)`.
- *Решение:* Запрошена очистка места на диске Mac (ожидаем).

**Next Steps (Следующие шаги):**
- Проверить авторизацию и выдачу кредитов в Supabase.
- Переименовать проект в интерфейсе на "ИИ с руками".
- Начать интеграцию с Vercel AI SDK (Оркестратор).
- Подключить генерацию каруселей через API.

---
*(Все записи ведутся на русском языке согласно глобальным правилам проекта).*
