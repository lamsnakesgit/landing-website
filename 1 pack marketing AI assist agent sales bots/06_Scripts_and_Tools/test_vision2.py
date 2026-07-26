import requests
import base64
import json

image_url = 'https://upload.wikimedia.org/wikipedia/ru/3/30/The_Matrix_poster.jpg'
image_data = requests.get(image_url).content
base64_image = base64.b64encode(image_data).decode('utf-8')

api_key = 'sk-8EobYRv3Rxkh5FWiEc735e5e391948569f3269Cf6273A9Ac'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

payload = {
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Что ты видишь на фото? Извлеки текст с афиши."
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
  "max_tokens": 500,
}

response = requests.post('https://api.aihubmix.com/v1/chat/completions', headers=headers, json=payload, timeout=20)
print("AIHubMix Status:", response.status_code)
print("AIHubMix Response:", response.text)

if response.status_code == 200:
    bot_token = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g'
    chat_id = '888005446'
    resp_data = response.json()
    msg = resp_data['choices'][0]['message']['content']
    tg_text = f"🤖 Привет! Это тест от Антигравити.\n\nЯ прогнал настоящую афишу (постер Матрицы) через AIHubMix (gpt-4o-mini). Всё работает идеально!\nВот что ответила модель:\n\n{msg}"
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': tg_text})
