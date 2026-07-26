#!/bin/bash
API_KEY="B6D711FCDE4D4FD5936544120E713976"
SERVER_URL="http://127.0.0.1:8080"
BOT_TOKEN="6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID="888005446"

# Fetch QR for number1
curl -s -X GET "$SERVER_URL/instance/connect/number1" -H "apikey: $API_KEY" > /tmp/qr1_new.json
# Fetch QR for number2
curl -s -X GET "$SERVER_URL/instance/connect/number2" -H "apikey: $API_KEY" > /tmp/qr2_new.json

cat /tmp/qr1_new.json | grep -o '"base64": *"[^"]*"' | cut -d'"' -f4 | sed 's/data:image\/png;base64,//g' > /tmp/qr1.b64
cat /tmp/qr2_new.json | grep -o '"base64": *"[^"]*"' | cut -d'"' -f4 | sed 's/data:image\/png;base64,//g' > /tmp/qr2.b64

base64 -d -i /tmp/qr1.b64 > /tmp/qr1.png
base64 -d -i /tmp/qr2.b64 > /tmp/qr2.png

curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto" -F chat_id=$CHAT_ID -F photo="@/tmp/qr1.png" -F caption="Свежий QR-код для Инстанса 1 (number1)" > /dev/null
curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto" -F chat_id=$CHAT_ID -F photo="@/tmp/qr2.png" -F caption="Свежий QR-код для Инстанса 2 (number2)" > /dev/null
