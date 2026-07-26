import os
import json
import time
import base64
import requests
import subprocess
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
PROJECT_ID = "gen-lang-client-0306422896" # from previous vertex_sa usage
LOCATION = "us-central1"

import google.auth
from google.auth.transport.requests import Request

def get_access_token():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), "vertex_sa.json")
    try:
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print("Error getting token:", e)
        return None

situations = [
    {
        "filename": "anime_poke_stick.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, looking desperate, gently poking a floating chat bubble with a long wooden stick. Clean solid white background. Lo-fi aesthetic, soft shading, high quality, suitable for a telegram sticker.",
        "text": "ПИКНИ, ЕСЛИ ЖИВОЙ 🥲"
    },
    {
        "filename": "anime_hourglass.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, looking sad, watching a giant glass hourglass where golden coins are pouring out instead of sand. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "А МЫ ВЕДЬ МОГЛИ УЖЕ ЗАПУСТИТЬСЯ... ⏳"
    },
    {
        "filename": "anime_lotus_dust.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, sitting peacefully in a zen lotus pose, covered in a light layer of dust and cobwebs, with an open laptop on her lap. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "Я ЖДУ ОПЛАТУ...\nИ Я БЕССМЕРТНА 🧘‍♀️"
    },
    {
        "filename": "anime_scroll.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, holding an endlessly unfurling scroll of paper that falls to the floor, looking extremely exhausted. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "ЕЩЁ ОДНА\nМАЛЕНЬКАЯ ПРАВОЧКА 📜"
    },
    {
        "filename": "anime_hacker.png",
        "prompt": "A cute anime-style girl with cool dark hacker glasses and casual stylish clothes, slamming her fist onto a giant red button, with bright digital matrix-style explosions of tech icons in the background. Clean solid white background. Lo-fi aesthetic.",
        "text": "ЩА НЕЙРОСЕТЬ\nВСЁ ПОШАМАНЯТ 🤖✨"
    },
    {
        "filename": "anime_microbudget.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, holding a giant magnifying glass to her eye, looking extremely disappointed at a microscopic gold coin. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "И ЭТО ВЕСЬ БЮДЖЕТ?! 🔍"
    },
    {
        "filename": "anime_drop_folder.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, dramatically slamming a heavy metal folder onto a desk, creating a shockwave impact. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "ЩА ПОКАЖУ,\nКАК ДЕЛАЮТ ПРОФИ 💥"
    },
    {
        "filename": "anime_rocket.png",
        "prompt": "A cute anime-style girl with big expressive eyes and casual stylish clothes, happily riding a shiny golden rocket that is smashing through a glass ceiling chart, flying upwards. Clean solid white background. Lo-fi aesthetic, soft shading, high quality.",
        "text": "ROI УЛЕТЕЛ В КОСМОС 🚀"
    }
]

PROJECT_ID = "my-project-28666-8-5-26-0-crm"

import google.auth
from google.auth.transport.requests import Request

def get_access_token():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), "vertex_sa.json")
    try:
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print("Error getting token:", e)
        return None

def generate_vertex_image(prompt_text, token):
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "instances": [{"prompt": prompt_text}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "outputOptions": {"mimeType": "image/png"}
        }
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Error from Vertex API: {resp.text}")
        return None
        
    data = resp.json()
    try:
        b64_data = data['predictions'][0]['bytesBase64Encoded']
        return base64.b64decode(b64_data)
    except Exception as e:
        print(f"Failed to parse Vertex response: {e}")
        return None

def process_and_watermark(image_bytes, output_path, text):
    try:
        img = Image.open(BytesIO(image_bytes))
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        draw = ImageDraw.Draw(img)
        try:
            # Use smaller font for multiline or long text
            font_size = 28 if "\n" in text or len(text) > 20 else 36
            font = ImageFont.truetype("Montserrat-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        # Draw text line by line if multiline
        lines = text.split("\n")
        total_h = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines) + 5 * (len(lines)-1)
        
        y_offset = 512 - total_h - 20
        shadow_color = (0, 0, 0, 180)
        outline_thickness = 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x = (512 - text_w) / 2
            
            for dx in [-outline_thickness, 0, outline_thickness]:
                for dy in [-outline_thickness, 0, outline_thickness]:
                    draw.text((x + dx, y_offset + dy), line, font=font, fill=shadow_color)
            
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += text_h + 5
            
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def send_to_tg(filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    print(f"Sending {filename} to TG...")
    with open(filename, 'rb') as f:
        resp = requests.post(
            url,
            data={'chat_id': CHAT_ID, 'caption': filename},
            files={'document': f}
        )
    return resp.json().get('ok')

if __name__ == "__main__":
    token = get_access_token()
    if not token:
        print("Failed to get token")
        exit(1)
        
    for item in situations:
        print(f"\n--- Generating {item['filename']} ---")
        img_bytes = generate_vertex_image(item['prompt'], token)
        if img_bytes:
            if process_and_watermark(img_bytes, item['filename'], item['text']):
                send_to_tg(item['filename'])
        print("Sleeping 6 seconds...")
        time.sleep(6) # Prevent quota issues
