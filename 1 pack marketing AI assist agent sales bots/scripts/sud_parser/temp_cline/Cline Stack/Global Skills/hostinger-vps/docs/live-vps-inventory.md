# Live VPS Inventory — Hostinger VPS

> Подтверждённый inventory по read-only аудиту VPS.
> Обновлено: 16.04.2026
> Source of truth = live VPS `<YOUR_VPS_IP>`

## Подключение
- Хост: `<YOUR_VPS_HOSTNAME>`
- IP: `<YOUR_VPS_IP>`
- SSH: `ssh -i ~/.ssh/id_ed25519 <SSH_USER>@<YOUR_VPS_IP>`
- OS: Ubuntu Linux `6.8.0-101-generic`

## Активные пользовательские и API-сервисы

| Сервис | Порт / URL | Путь | Runtime / способ запуска | Статус |
|---|---|---|---|---|
| N8N main | `127.0.0.1:5678` | `/docker/n8n` | Docker | Активен |
| N8N worker | internal | `/docker/n8n` | Docker | Активен |
| N8N ffmpeg | `<YOUR_N8N_DOMAIN>` | `/docker/n8n` | Docker | Активен |
| Traefik gateway | `80`, `443` | `/docker/n8n` | Docker | Активен |
| Redis | internal `6379` | `/docker/n8n` | Docker | Активен |
| N8N Postgres | internal `5432` | `/docker/n8n` | Docker | Активен |
| LiteLLM API | `32779`, `https://<YOUR_LITELLM_API_DOMAIN>` | `/docker/litellm-xne6` | Docker | Активен |
| LiteLLM public canary | `32789` | `/docker/litellm-xne6` | Docker | Активен |
| LiteLLM public-only canary | `32790` | `/docker/litellm-xne6` | Docker | Активен |
| LiteLLM Postgres | internal `5432` | `/docker/litellm-xne6` | Docker | Активен |
| Open WebUI | `3000`, `https://<YOUR_OPEN_WEBUI_DOMAIN>` | `/docker/openwebui-litellm` | Docker | Активен |
| Shlink API | `32775`, `https://<YOUR_SHLINK_API_DOMAIN>` | `/docker/shlink-by0k` | Docker | Активен |
| Shlink Web UI | `32776`, `https://<YOUR_SHLINK_WEB_DOMAIN>` | `/docker/shlink-by0k` | Docker | Активен |
| Billing Portal | `127.0.0.1:8002`, `https://<YOUR_BILLING_DOMAIN>` | `/opt/billing-portal` | Docker | Активен |
| SearXNG | `8888` | `/opt/searxng` | Docker | Активен |
| Scraper Server | `9111` | `/opt/scraper-server` | Docker | Активен |
| Invidious | `3001` | `/opt/invidious` | Docker | Активен |
| Invidious Companion | `127.0.0.1:8282` | `/opt/invidious` | Docker | Активен |
| Invidious DB | internal `5432` | `/opt/invidious` | Docker | Активен |
| YT Transcript | `9222` | `/opt/yt-transcript` | Docker | Активен |
| Whisper ASR | `9000` | `/opt/docker-compose` | Docker | Активен |
| Agent Capture API | `7788` | `/opt/agent-capture-api` | Docker | Активен |
| TickTick MCP Server | `9333` | `/opt/ticktick-mcp-server` | Docker | Активен |
| Telegram API Engine | `8000` | `/opt/telegram-api-engine` | Python / Uvicorn процесс | Активен как процесс, но systemd unit inactive |
| ProAI Bot | `8080` | `/opt/proai-bot` | systemd + Python | Активен |
| Telegram Cline Bot | PM2 process | PM2 | PM2 | Активен |

## Внутренние wrapper / agent-сервисы

| Сервис | Порт | Путь | Runtime | Статус |
|---|---|---|---|---|
| Cline Wrapper | `3333` | `/opt/cline-agent` | PM2 + Node.js | Активен |
| Claude CLI Wrapper | `8787` | `/opt/claude-cli-wrapper` | Node.js | Активен |
| Codex CLI Wrapper | `8788` | `/opt/codex-cli-wrapper` | systemd + Node.js | Активен |
| Codex CLI Wrapper Bridge | bridge to `8788` | `/opt/codex-cli-wrapper` | systemd + Python | Активен |
| CLIProxyAPI | `127.0.0.1:1455`, `127.0.0.1:8317` | `/opt/cliproxyapi` | Docker | Активен |
| Claude relay container | internal only | `/docker/claude-cli-wrapper-relay` | Docker / Caddy | Активен |
| Codex relay container | internal only | `/docker/codex-cli-wrapper-relay` | Docker / Caddy | Активен |
| ProAI bot relay | internal only | `/opt/proai-bot-relay` | Docker / Caddy | Активен |

## Присутствуют на VPS, но не подтверждены как активные product-сервисы

| Объект | Путь | Статус / комментарий |
|---|---|---|
| telegram-listener.service | systemd | Установлен и enabled, но сейчас inactive |
| telegram-api-engine.service | systemd | Установлен и enabled, но сейчас inactive; сам API при этом запущен отдельным uvicorn-процессом |
| telegram-bot | `/opt/telegram-bot` | Папка существует, активный сервис не подтверждён |
| metube | `/opt/metube` | Папка существует, активный контейнер не подтверждён |
| github-runner | `/opt/github-runner` | Служебная директория |
| cubence-agent-sdk-test | `/opt/cubence-agent-sdk-test` | Тестовая директория |
| firefox-config | `/opt/firefox-config` | Служебная директория |
| containerd | `/opt/containerd` | Системная / служебная директория |
| whisper-cache | `/opt/whisper-cache` | Кэш / служебная директория |
| billing-test | `/docker/billing-test` | Лежит на диске, как active сервис не подтверждён |
| billing-test backup | `/docker/billing-test.bak.20260324_214309` | Бэкап |
| billing-portal archive | `/docker/billing-portal_archive_20260327_205918` | Архив |

## Подтверждённые места хранения ключей
- Scraper Server → `FEWSATS_SCRAPER_API_KEY` в `/opt/scraper-server/docker-compose.yml`
- Telegram API Engine → `API_KEY` в `/opt/telegram-api-engine/.env`
- Shlink → `INITIAL_API_KEY` в `/docker/shlink-by0k/.env`, затем пробрасывается в `docker-compose.yml`
- SearXNG → без аутентификации

## Полезные URL и внутренние endpoints
- SearXNG → `http://<YOUR_VPS_IP>:8888/search?q={query}&format=json&language=ru`
- Scraper → `POST http://<YOUR_VPS_IP>:9111/v0/scrape`
- Invidious search → `GET http://<YOUR_VPS_IP>:3001/api/v1/search?q={query}&type=video`
- Invidious video → `GET http://<YOUR_VPS_IP>:3001/api/v1/videos/{videoId}`
- YT Transcript → `GET http://<YOUR_VPS_IP>:9222/transcript/{videoId}?lang=en&format=text`
- Telegram API Engine → `http://<YOUR_VPS_IP>:8000`
- Agent Capture API → `http://<YOUR_VPS_IP>:7788`
- Shlink API → `http://<YOUR_VPS_IP>:32775/rest/v3/short-urls`
- Shlink Web UI → `https://<YOUR_SHLINK_WEB_DOMAIN>`
- LiteLLM API → `https://<YOUR_LITELLM_API_DOMAIN>` / `http://127.0.0.1:32779`
- Open WebUI → `https://<YOUR_OPEN_WEBUI_DOMAIN>`
- Billing Portal → `https://<YOUR_BILLING_DOMAIN>` / `http://127.0.0.1:8002`
- Cline Wrapper → `http://127.0.0.1:3333`
- Claude CLI Wrapper → `http://0.0.0.0:8787`
- Codex CLI Wrapper → `http://127.0.0.1:8788`
- CLIProxyAPI → `http://127.0.0.1:8317` + callback `1455`
- TickTick MCP Server → `http://<YOUR_VPS_IP>:9333`

## Быстрые read-only команды аудита
```bash
# Активные контейнеры
docker ps

# Все контейнеры
docker ps -a

# Прослушиваемые порты
ss -tulpn | grep LISTEN

# Running systemd services
systemctl list-units --type=service --state=running --no-pager

# PM2
pm2 list

# compose/env inventory
find /opt /docker -maxdepth 2 \( -name docker-compose.yml -o -name compose.yml -o -name compose.yaml -o -name .env -o -name "*.env" \)
```
