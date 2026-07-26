#!/bin/bash

API_KEY="B6D711FCDE4D4FD5936544120E713976"
SERVER_URL="http://127.0.0.1:8080"

# Create first instance
curl -s -X POST "$SERVER_URL/instance/create" \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "number1",
    "token": "token1",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }' > /tmp/instance1.json

echo ""

# Create second instance
curl -s -X POST "$SERVER_URL/instance/create" \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "number2",
    "token": "token2",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }' > /tmp/instance2.json

echo ""

# Extract QR code base64 from json
cat /tmp/instance1.json | grep -o '"base64": *"[^"]*"' | cut -d'"' -f4 > /tmp/qr1.b64
cat /tmp/instance2.json | grep -o '"base64": *"[^"]*"' | cut -d'"' -f4 > /tmp/qr2.b64

cat /tmp/instance1.json
echo ""
cat /tmp/instance2.json
