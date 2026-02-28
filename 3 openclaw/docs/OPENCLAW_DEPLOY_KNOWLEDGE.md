# База знаний по развертыванию OpenClaw (Holy Knowledge)

Этот документ содержит критически важную информацию для настройки новых VPS серверов для клиентов. Он решает все неочевидные проблемы "из коробки" (порты, WebSocket, TTS).

## 1. Порты и Web UI
Главная проблема при деплое — путаница с портами.
- `3000` — часто занят другими сервисами (например, WhatsApp шлюзами типа GoWA).
- `8080` — обычно используется для FileBrowser (файловый менеджер).
- `3001` — API Gateway (не отдаёт графический интерфейс, выдает "Cannot GET /chat").
- **`18789`** — Реальный порт, на котором по умолчанию крутится Control UI (графический дашборд OpenClaw).

**Правило:** В конфигурации Nginx (proxy_pass) всегда указывайте `http://127.0.0.1:18789;`.

## 2. Ошибка WebSocket 1008 (Secure Context / Untrusted Proxy)
Даже если Nginx пробросит порт 18789, дашборд не пустит пользователя, выдавая ошибку `disconnected (1008): control ui requires HTTPS or localhost (secure context)`.

**Причины и решения:**
1. **Отсутствие строгих заголовков HTTPS в Nginx**: OpenClaw должен понимать, что клиент сидит защищенно (по HTTPS). В `location /` обязательно должны быть:
   ```nginx
   proxy_set_header X-Forwarded-Proto https;
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection "upgrade";
   ```
2. **Недоверенный IP Nginx**: OpenClaw блокирует прокси, если его нет в белом списке. Необходимо прописать `127.0.0.1` в `gateway.trustedProxies`.
   *Команда:* `docker exec openclaw node dist/index.js config set gateway.trustedProxies '["127.0.0.1"]'`

## 3. Ошибка TTS (Text-to-Speech) и отсутствие звука
По умолчанию в OpenClaw конфигурация TTS может отсутствовать или быть сломанной. Бот пытается читать русские буквы английским движком и замолкает. Вторая частая проблема — попытка прописать конфиг `tts` в корень файла `openclaw.json` (что вызывает вечный цикл перезагрузки контейнера — Fatal Error).

**Правило:** Конфигурация TTS находится **только** по пути `messages.tts`.

Для бесплатного и качественного русского голоса (Светлана от Microsoft Edge) нужно прописать 3 параметра через CLI:
```bash
docker exec openclaw node dist/index.js config set messages.tts.provider "edge"
docker exec openclaw node dist/index.js config set messages.tts.auto "always"
docker exec openclaw node dist/index.js config set messages.tts.edge "{\"enabled\":true,\"lang\":\"ru-RU\",\"voice\":\"ru-RU-SvetlanaNeural\"}"
```

## 4. Заблокированная команда /restart
Команда `/restart` в Telegram по умолчанию выключена в целях безопасности.
Ее нужно включить через CLI:
```bash
docker exec openclaw node dist/index.js config set commands.restart true
```

---
*Скрипт автоматической починки всех этих багов за 1 секунду находится в файле `scripts/setup_client_vps.sh`.*
