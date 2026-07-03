# Технический стек и инфраструктура

> Короткая оперативная выжимка по стеку пользователя.
> Для серверных, VPS, Docker и инфраструктурных задач source of truth = live VPS + подтверждённый read-only аудит.
> Для полного списка сервисов и актуального inventory используй skill `hostinger-vps` и читай `docs/live-vps-inventory.md` внутри skill.

---

## Технический стек

| Область | Технологии |
|---|---|
| **Backend** | Python (FastAPI/Uvicorn), Node.js / TypeScript |
| **Автоматизация** | N8N (self-hosted на VPS), воркеры, ffmpeg-instance |
| **AI/LLM infra** | LiteLLM, Open WebUI, Cline Wrapper, Claude CLI Wrapper, Codex CLI Wrapper, CLIProxyAPI |
| **БД / очереди** | PostgreSQL, Redis, SQLite (точечно), Docker volumes |
| **Телеграм** | aiogram / python-telegram-bot, Telegram API Engine, ProAI Bot, Telegram Cline Bot |
| **Поиск и контент** | SearXNG, Scraper Server, Invidious, YT Transcript, Whisper ASR |
| **Утилиты** | Shlink, Billing Portal, Agent Capture API, TickTick MCP |
| **Оркестрация и runtime** | Docker Compose, Traefik, Caddy, systemd, PM2 |
| **Деплой** | Railway (для части проектов), Hostinger VPS, Docker |

---

## Hostinger VPS — краткое оглавление

### Подключение
- **Хост:** `<YOUR_VPS_HOSTNAME>`
- **IP:** `<YOUR_VPS_IP>`
- **SSH:** `ssh -i ~/.ssh/id_ed25519 <SSH_USER>@<YOUR_VPS_IP>`
- **OS:** Ubuntu Linux 6.8.0-101-generic

### Что сейчас активно на VPS
- **N8N stack:** main, worker, ffmpeg, Traefik, Redis, Postgres
- **LiteLLM stack:** LiteLLM API, public canary, public-only canary, Postgres
- **AI/UI:** Open WebUI
- **Search/content:** SearXNG, Scraper Server, Invidious, Invidious Companion, YT Transcript, Whisper ASR
- **Utilities:** Shlink API, Shlink Web UI, Billing Portal, Agent Capture API, TickTick MCP Server
- **Telegram/runtime:** Telegram API Engine, ProAI Bot, Telegram Cline Bot
- **Wrappers/internal:** Cline Wrapper, Claude CLI Wrapper, Codex CLI Wrapper, Codex bridge, CLIProxyAPI, relay containers

### Полезные публичные URL
- **N8N:** `https://<YOUR_N8N_DOMAIN>`
- **LiteLLM API:** `https://<YOUR_LITELLM_API_DOMAIN>`
- **Open WebUI:** `https://<YOUR_OPEN_WEBUI_DOMAIN>`
- **Billing Portal:** `https://<YOUR_BILLING_DOMAIN>`
- **Shlink short URLs:** `https://<YOUR_SHLINK_API_DOMAIN>`
- **Shlink Web UI:** `https://<YOUR_SHLINK_WEB_DOMAIN>`

### Подтверждённые места хранения ключей
- **Scraper Server:** `FEWSATS_SCRAPER_API_KEY` в `/opt/scraper-server/docker-compose.yml`
- **Telegram API Engine:** `API_KEY` в `/opt/telegram-api-engine/.env`
- **Shlink:** `INITIAL_API_KEY` в `/docker/shlink-by0k/.env`
- **SearXNG:** без аутентификации

### Безопасный шаблон секретов
```env
SCRAPER_SERVER_TOKEN=<stored in secrets>
TELEGRAM_API_TOKEN=<stored in secrets>
SHLINK_API_KEY=<stored in secrets>
```

### Где лежит полный inventory
- **Skill:** `hostinger-vps`
- **Файл:** `~/.agents/skills/hostinger-vps/docs/live-vps-inventory.md`

---

## MCP серверы (настроенные в Cline)

| MCP сервер | Назначение | Ключевые инструменты |
|---|---|---|
| **Tavily** | Поиск, извлечение, краулинг, исследования | `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research` |
| **Context7** | Документация библиотек | `resolve-library-id`, `query-docs` |
| **GitHub** | Репозитории, код, issues, PR | `get_file_contents`, `search_code`, `search_issues` |
| **Railway** | Деплой, сервисы, переменные | `deploy`, `list-services`, `get-logs` |
| **N8N Docs** | Документация + валидация n8n нод | `search_nodes`, `get_node`, `validate_node`, `validate_workflow`, `search_templates`, `get_template` |

---

## Документация на Desktop (*.md файлы)

> Наличие markdown-файла на Desktop не означает, что соответствующий сервис активен сейчас на VPS.

| Файл | Описание |
|---|---|
| `SCRAPER-SERVER-ИНСТРУКЦИЯ.md` | Полная документация Scraper Server API |
| `INVIDIOUS-ИНСТРУКЦИЯ.md` | Документация Invidious + YT Transcript |
| `SEARXNG-API-ПРИМЕРЫ.md` | Примеры SearXNG запросов на разных языках |
| `SEARXNG-ADVANCED-SETTINGS.md` | Продвинутые настройки SearXNG |
| `SEARXNG-PROJECT.md` | Обзор проекта SearXNG |
| `N8N-HTTP-SEARXNG.md` | Настройка SearXNG в N8N |
| `N8N-SEARXNG-FORUMS.md` | Поиск по форумам через SearXNG + N8N |
| `N8N-TELEGRAM-PARSER.md` | Telegram-парсер через N8N |
| `TAVILY-SOURCES.md` | Справочник источников для Tavily |
| `N8N-STACK-SCHEMA.md` | Схема N8N-стека — MCP + Skills |
| `SHLINK-ИНСТРУКЦИЯ.md` | Документация Shlink API для сокращения URL |

---

*Последнее live-обновление по read-only аудиту VPS: 16.04.2026*
