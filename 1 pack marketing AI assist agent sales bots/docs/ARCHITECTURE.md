# ARCHITECTURE
Описание ключевых архитектурных решений проекта.

## 2026-04-12
- Полный отказ от Google Apps Script для рассылок (перенос всей логики масштабирования и обработки в n8n). На стороне Google сохраняется только статус БД.
- Использование "Spec-First" методологии при расширении API.
- Перешли на файловую структуру с 6 основными доменами: AI, Web, Marketing, Media, N8N, Scripts.

## 2026-05-16
- Для персонального и бизнес-ассистента принято гибридное решение: **Hermes = основной интерфейс и агент в Telegram**, **n8n = оркестратор интеграций, фоновых процессов и event-driven automation**, **Supabase = операционная память, RAG-слой и хранилище артефактов**.
- Архитектура строится не как один монолитный бот, а как набор контуров: `Telegram intake`, `memory/RAG`, `tool execution`, `meeting intelligence`, `content studio`, `business ops integrations`.
- Мультимодальность должна быть native-first: текст, voice, audio, документы, ссылки на видео, далее расширение до video/video_note и внешних meeting sources (Fathom/Zoom).
- Контур встреч проектируется webhook-first: **Fathom/Zoom → n8n ingest → normalization → summary/timecodes/action items → Telegram/Notion/Asana delivery**.
- Для групповых чатов и мониторинга диалогов рекомендован отдельный operational контур/агент с собственными правилами доступа и triage-логикой, а не смешивание всего в одном личном потоке Hermes.
- По внешним источникам и official docs подтверждено, что **Hermes лучше подходит как personal/business executive assistant**, если приоритеты — долговременная память, Telegram/VPS-режим, skill-learning, cron automation и MCP-расширяемость.
- **OpenClaw** остаётся сильным вариантом для multi-agent orchestration, dashboard-heavy сценариев и широкого ecosystem/community tooling, но требует более жёсткого security hardening и аккуратного контроля skills/plugins.
- Практический вывод для этого проекта: **ставить Hermes как основной агент**, а **n8n использовать как интеграционный backbone**; OpenClaw рассматривать только как отдельный future-layer для специализированных swarm/monitoring сценариев.
- Для учёта расходов нужен отдельный cost/usage слой: Hermes/OpenRouter или прямые провайдеры для inference, Supabase/Postgres таблицы для логирования вызовов, бюджеты по task-type и отдельные routing-правила по моделям.

## 2026-05-24
- Внедрён контур удалённого управления воркспейсом через приватного Telegram ИИ-агента (`telegram_agent_bot.py`). Архитектура построена на базе OpenAI Tool Calling и прямого выполнения shell-команд, чтения/записи файлов на локальном Mac. Безопасность обеспечивается строгой валидацией по ID пользователя в Telegram на уровне вебхука/polling-обработчика.
- Журнал РНП переведён на табличный лог-формат в Markdown (`rnp_log.md`), что позволяет просто парсить его регулярными выражениями или скриптами и легко редактировать вручную.
