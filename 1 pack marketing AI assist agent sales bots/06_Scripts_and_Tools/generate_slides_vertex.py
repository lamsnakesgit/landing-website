import google.auth
from google.auth.transport.requests import Request
import requests
import json
import os
import base64

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"

credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

locations = ["us-east4", "us-west1", "europe-west1", "europe-west4", "asia-southeast1", "us-central1"]

TELEGRAM_BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
TG_CHAT_ID_MAIN = "888005446"

prompts = [
    {
        "name": "Slide 4",
        "prompt": "Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay exactly reads: \"СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ\". Cyberpunk, high contrast, symbol of rebellion. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe\"."
    },
    {
        "name": "Slide 5",
        "prompt": "Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay exactly reads: \"OPEN-SOURCE РВЕТ GPT\". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe\"."
    },
    {
        "name": "Slide 6",
        "prompt": "Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon typography text in the background exactly reads: \"ПИШИ: ОТКРЫТЫЙ\". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe\"."
    }
]

def send_to_tg(image_bytes, caption):
    files = {'photo': ('image.png', image_bytes, 'image/png')}
    data = {'chat_id': TG_CHAT_ID_MAIN, 'caption': caption}
    r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", files=files, data=data)
    print("Telegram Response:", r.status_code)

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; charset=utf-8"
}

for p in prompts:
    print(f"Generating {p['name']}...")
    success = False
    for loc in locations:
        url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{loc}/publishers/google/models/imagen-3.0-generate-001:predict"
        data = {
            "instances": [{"prompt": p["prompt"]}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "3:4"
            }
        }
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            res_json = res.json()
            if 'predictions' in res_json and len(res_json['predictions']) > 0:
                b64_img = res_json['predictions'][0]['bytesBase64Encoded']
                image_bytes = base64.b64decode(b64_img)
                print(f"Generated {p['name']} using region {loc}")
                send_to_tg(image_bytes, p['name'] + " (Only Headline)")
                success = True
                break
            else:
                print(f"Failed to get prediction for {p['name']} in region {loc}")
        else:
            print(f"Region {loc} returned {res.status_code}")
    
    if not success:
        print(f"Failed to generate {p['name']} across all regions.")
