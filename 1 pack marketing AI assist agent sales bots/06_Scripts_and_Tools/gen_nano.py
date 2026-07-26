import os
import json
import requests
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def generate_image():
    creds = service_account.Credentials.from_service_account_file(
        'vertex_sa.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    creds.refresh(Request())
    token = creds.token
    project_id = 'my-project-97115-216-254'
    model_id = 'gemini-3.1-flash-image'
    
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/{model_id}:generateContent"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    prompt = """A futuristic promotional poster for an AI workshop. 
On the left, an Asian woman in a black turtleneck suit holding a black coffee cup, surrounded by futuristic robotic hands and a glowing digital brain hologram. 
On the right, typography text overlay exactly reads:
"ВАЙБ-КОДИНГ"
"АГЕНТЫ"
"И МЕССЕНДЖЕРЫ"
Bullet points text exactly reads:
"- Подключаем агента к Telegram/WhatsApp"
"- Настройка без кода — вайб-кодинг"
"- Живое демо прямо на эфире"
"- Разберём ваши кейсы"

At the bottom in a bright cyan banner, large typography text exactly reads: "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН".
At the very bottom, small typography text exactly reads: "TG: @nnsvt".
Dark blue and purple neon aesthetic, tech corporate vibe, high resolution."""
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"]
        }
    }
    
    print("Sending request to Nano Banana 2...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        try:
            b64 = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
            with open('nano_banana_output.jpg', 'wb') as f:
                f.write(base64.b64decode(b64))
            print("Image saved as nano_banana_output.jpg")
        except Exception as e:
            print("Error parsing image data:", e)
            print(json.dumps(data, indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == '__main__':
    generate_image()
