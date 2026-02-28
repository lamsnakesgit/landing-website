#!/bin/bash

# ==============================================================================
# OpenClaw Fast Deploy Script (Fixes: UI Port, WebSockets, TTS, Restart)
# Run this on a fresh Ubuntu Server where OpenClaw Docker is running.
# ==============================================================================

# Задаем домен (для Nginx и Certbot)
DOMAIN=$1
ADMIN_EMAIL=$2

if [ -z "$DOMAIN" ] || [ -z "$ADMIN_EMAIL" ]; then
    echo "Usage: ./setup_client_vps.sh <domain.com> <admin@email.com>"
    exit 1
fi

echo "=========================================================="
echo "🚀 1/4 Setup Nginx Reverse Proxy for $DOMAIN (Port 18789)"
echo "=========================================================="

cat << EOF > /etc/nginx/sites-available/openclaw.conf
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:18789;
        
        # Важные заголовки для обхода защиты OpenClaw WebSocket
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # (Опционально) Basic Auth uncomment below
        # auth_basic "Restricted Access";
        # auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF

ln -sf /etc/nginx/sites-available/openclaw.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "=========================================================="
echo "🔐 2/4 Issuing SSL Certificate via Certbot"
echo "=========================================================="
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $ADMIN_EMAIL

echo "=========================================================="
echo "🤖 3/4 Injecting OpenClaw Config Fixes (TTS, Proxies, Restart)"
echo "=========================================================="

# 1. Добавляем 127.0.0.1 в доверенные прокси (убираем ошибку WebSocket 1008)
docker exec openclaw node dist/index.js config set gateway.trustedProxies '["127.0.0.1"]'

# 2. Включаем команду /restart в Telegram
docker exec openclaw node dist/index.js config set commands.restart true

# 3. Устанавливаем русский TTS (Edge)
docker exec openclaw node dist/index.js config set messages.tts.provider "edge"
docker exec openclaw node dist/index.js config set messages.tts.auto "always"
docker exec openclaw node dist/index.js config set messages.tts.edge "{\"enabled\":true,\"lang\":\"ru-RU\",\"voice\":\"ru-RU-SvetlanaNeural\"}"

echo "=========================================================="
echo "🔄 4/4 Restarting OpenClaw Docker Container"
echo "=========================================================="
# Замените путь ниже, если docker-compose лежит в другом месте!
docker compose -f /root/openclaw/docker-compose.yml restart openclaw

echo "✅ Setup Complete! Your Agent is now Secure, Russian-speaking, and UI is live at https://$DOMAIN"
