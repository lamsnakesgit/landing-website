import os
import time
import base64
import requests
import google.auth
from google.auth.transport.requests import Request
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"

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
        "filename": "cine_poke.png",
        "prompt": "A cinematic hyper-realistic portrait of an exhausted modern businesswoman sitting in a dark office at night, looking desperate with bags under her eyes, pointing a pen at a floating holographic chat bubble that has no reply. Messy desk, empty coffee cups. High end photography, dramatic neon lighting, highly detailed, 8k.",
        "text": "ПИКНИ,\nЕСЛИ ЖИВОЙ 🥲"
    },
    {
        "filename": "cine_hourglass.png",
        "prompt": "A cinematic hyper-realistic portrait of a stressed modern businesswoman in a dark office, looking sadly at a large glowing hourglass filled with golden coins slipping away. Face illuminated by screen glow, messy hair. High end photography, dramatic neon lighting.",
        "text": "А МЫ ВЕДЬ МОГЛИ\nУЖЕ ЗАПУСТИТЬСЯ... ⏳"
    },
    {
        "filename": "cine_lotus.png",
        "prompt": "A cinematic hyper-realistic portrait of an exhausted but calm modern businesswoman meditating in a zen pose in a dark office, covered in a light layer of dust and cobwebs, waiting for a payment. High end photography, dramatic moody lighting.",
        "text": "Я ЖДУ ОПЛАТУ...\nИ Я БЕССМЕРТНА 🧘‍♀️"
    },
    {
        "filename": "cine_scroll.png",
        "prompt": "A cinematic hyper-realistic portrait of a crying modern businesswoman in a dark office, holding her head in her hands while looking at an impossibly long glowing holographic scroll of text edits unfurling on her desk. Empty coffee cups, stress. High end photography, dramatic neon lighting.",
        "text": "ЕЩЁ ОДНА\nМАЛЕНЬКАЯ ПРАВОЧКА 📜"
    },
    {
        "filename": "cine_hacker.png",
        "prompt": "A cinematic hyper-realistic portrait of an excited, slightly mad modern businesswoman wearing futuristic smart glasses, aggressively smashing a glowing red holographic button, with matrix code raining down. High end photography, cinematic lighting.",
        "text": "ЩА НЕЙРОСЕТЬ\nВСЁ ПОШАМАНЯТ 🤖✨"
    },
    {
        "filename": "cine_microbudget.png",
        "prompt": "A cinematic hyper-realistic portrait of an extremely disappointed modern businesswoman in a dark office, looking through a glowing magnifying glass at a single microscopic gold coin. Dramatic shadows, frustrated expression. High end photography, dramatic neon lighting.",
        "text": "И ЭТО\nВЕСЬ БЮДЖЕТ?! 🔍"
    },
    {
        "filename": "cine_drop_folder.png",
        "prompt": "A cinematic hyper-realistic portrait of a fiercely determined modern businesswoman in a dark office, aggressively slamming a heavy glowing tablet onto a glass desk, causing a shockwave. Powerful expression. High end photography, dramatic lighting.",
        "text": "ЩА ПОКАЖУ,\nКАК ДЕЛАЮТ ПРОФИ 💥"
    },
    {
        "filename": "cine_rocket.png",
        "prompt": "A cinematic hyper-realistic portrait of a wildly happy, ecstatic modern businesswoman in a dark office, looking up at a glowing golden holographic rocket launching through a digital stock chart going up. High end photography, dramatic neon lighting.",
        "text": "ROI УЛЕТЕЛ\nВ КОСМОС 🚀"
    }
]

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
            font_size = 28 if "\n" in text or len(text) > 20 else 36
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
        except Exception as e:
            print(f"Font error: {e}")
            try:
                font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
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
        print("Sleeping 65 seconds to avoid Quota limits...")
        time.sleep(65)
