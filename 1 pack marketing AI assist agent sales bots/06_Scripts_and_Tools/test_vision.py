import requests
import base64
import json
import os

# Download a sample poster (e.g., a simple movie poster)
image_url = 'https://upload.wikimedia.org/wikipedia/ru/3/30/The_Matrix_poster.jpg'
image_data = requests.get(image_url).content
base64_image = base64.b64encode(image_data).decode('utf-8')

# Try GRSAI first
grsai_key = 'sk-55b4bfc2dfdf48bc92678dab6aa679af'
headers = {
    'Authorization': f'Bearer {grsai_key}',
    'Content-Type': 'application/json'
}

payload = {
  "model": "gemini-2.5-flash",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Что ты видишь на фото? Пожалуйста, извлеки весь текст с афиши."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 1500,
  "temperature": 0.2
}

try:
    response = requests.post('https://api.grsai.com/v1/chat/completions', headers=headers, json=payload, timeout=20)
    print("GRSAI Status:", response.status_code)
    print("GRSAI Response:", response.text)
except Exception as e:
    print("Error calling GRSAI:", e)

# Send result to user via Telegram
bot_token = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g'
chat_id = '888005446'

# Try OpenRouter with a free model if GRSAI fails
# But let's just send the result of GRSAI first to telegram
tg_text = f"Привет! Это Антигравити.\nЯ только что протестировал API GRSAI (gemini-2.5-flash) с НАСТОЯЩЕЙ картинкой в base64 (постер Матрицы).\n\nРезультат: {response.text[:500]}"
requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': tg_text})

