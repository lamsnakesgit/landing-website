# База знаний по развертыванию OpenClaw (Holy Knowledge)

## 1. Порты и Web UI
- **`18789`** — Реальный порт для Control UI (Web Dashboard).
- В Nginx (proxy_pass) указывайте `http://127.0.0.1:18789;`.

## 2. WebSocket 1008 (Secure Context)
OpenClaw блокирует WebSocket без HTTPS. В Nginx обязательно:
```nginx
proxy_set_header X-Forwarded-Proto https;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```
Также пропишите `127.0.0.1` в `gateway.trustedProxies`.

## 3. Русский голос (TTS Edge)
Конфигурация находится в `messages.tts`.
```bash
docker exec openclaw node dist/index.js config set messages.tts.provider "edge"
docker exec openclaw node dist/index.js config set messages.tts.edge "{\"enabled\":true,\"lang\":\"ru-RU\",\"voice\":\"ru-RU-SvetlanaNeural\"}"
```
