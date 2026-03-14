#!/bin/bash
# Скрипт быстрой автонастройки клиента (OpenClaw)
DOMAIN=$1
ADMIN_EMAIL=$2

# Настройка Nginx и SSL
# ... (код проксирования на 18789 с WebSocket заголовками) ...

# Настройка OpenClaw через Docker Exec
docker exec openclaw node dist/index.js config set gateway.trustedProxies '["127.0.0.1"]'
docker exec openclaw node dist/index.js config set commands.restart true
docker exec openclaw node dist/index.js config set messages.tts.provider "edge"
docker exec openclaw node dist/index.js config set messages.tts.auto "always"
docker exec openclaw node dist/index.js config set messages.tts.edge "{\"enabled\":true,\"lang\":\"ru-RU\",\"voice\":\"ru-RU-SvetlanaNeural\"}"

docker compose -f /root/openclaw/docker-compose.yml restart openclaw
echo "✅ Клиент настроен!"
