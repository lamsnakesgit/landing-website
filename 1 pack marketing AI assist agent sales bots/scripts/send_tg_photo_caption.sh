#!/bin/bash

# Скрипт для отправки фото с длинным описанием (caption) через Telegram API.
# Используется метод sendPhoto вместо sendMessage.
# Параметр parse_mode="Markdown" или "HTML" позволяет форматировать текст.

BOT_TOKEN="ВАШ_ТОКЕН"
CHAT_ID="ВАШ_CHAT_ID"
PHOTO_PATH="/путь/к/картинке.png"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
  -F chat_id="${CHAT_ID}" \
  -F photo="@${PHOTO_PATH}" \
  -F parse_mode="Markdown" \
  -F caption="⚡️ *Жирный заголовок* ⚡️

Обычный текст с описанием поста. Можно использовать эмодзи и абзацы.
— Буллит 1
— Буллит 2

👇 *Пиши в ЛС:*
🔗 https://t.me/your_link"
