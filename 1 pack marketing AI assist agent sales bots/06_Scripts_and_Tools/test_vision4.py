import requests
import base64
import json

image_url = 'https://upload.wikimedia.org/wikipedia/ru/3/30/The_Matrix_poster.jpg'
image_data = requests.get(image_url).content
base64_image = base64.b64encode(image_data).decode('utf-8')

google_key = 'AIzaSyACWHFb9ud11-0_XFaeFWDVw9Iyg-KTS9k'
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={google_key}'
headers = {'Content-Type': 'application/json'}

payload = {
  "contents": [{
    "parts":[
      {"text": "Что ты видишь на фото? Извлеки текст с афиши."},
      {
        "inline_data": {
          "mime_type":"image/jpeg",
          "data": base64_image
        }
      }
    ]
  }]
}

response = requests.post(url, headers=headers, json=payload, timeout=20)
print("Gemini Status:", response.status_code)

if response.status_code == 200:
    bot_token = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g'
    chat_id = '888005446'
    resp_data = response.json()
    msg = resp_data['candidates'][0]['content']['parts'][0]['text']
    tg_text = f"🤖 БИНГО! Это тест от Антигравити.\n\nЯ только что прогнал картинку-постер через официальный Google Gemini. \nGRSAI реально сломан, а AIHubMix пустой, но сам код со зрением работает идеально!\n\nВот что ответила нейросеть по картинке:\n\n{msg}"
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': tg_text})
else:
    print("Gemini Response:", response.text)
