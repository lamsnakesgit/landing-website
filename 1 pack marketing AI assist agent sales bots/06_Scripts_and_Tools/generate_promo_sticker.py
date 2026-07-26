import os
import requests
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import google.auth
from google.auth.transport.requests import Request

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"

BOT_TOKEN_SEND = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # openantigravitybot
USER_ID = "450206471"

# --- 1. PROMPT ---
prompt = (
    "A cinematic high-quality rendering in the style of The Matrix. "
    "A slightly dark-skinned young woman, wearing stylish glasses and a prominent ring on her RIGHT INDEX FINGER. "
    "She is wearing a sleek black trench coat. She is holding out her open hand towards the camera, "
    "offering a glowing RED PILL. Mysterious and inviting cinematic lighting."
)
text = "ХОЧУ АРМИЮ\\nИИ-АГЕНТОВ 💊"

# --- 2. AUTH ---
credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())
location = "us-central1"
vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/imagen-3.0-generate-001:predict"

def generate_image_vertex(prompt, output_filename):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}
    }
    
    print(f"Generating image: {output_filename}...")
    response = requests.post(vertex_url, headers=headers, json=data)
    if response.status_code == 200:
        res_json = response.json()
        b64 = res_json['predictions'][0]['bytesBase64Encoded']
        with open(output_filename, "wb") as f:
            f.write(base64.b64decode(b64))
        return True
    else:
        print(f"Failed to generate {output_filename}: {response.text}")
        return False

def draw_text(draw, text, font, width, y_pos):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x_pos = (width - text_w) / 2
    
    stroke_color = "black"
    stroke_width = 4
    for dx in range(-stroke_width, stroke_width+1):
        for dy in range(-stroke_width, stroke_width+1):
            if dx*dx + dy*dy <= stroke_width*stroke_width:
                draw.text((x_pos+dx, y_pos+dy), text, font=font, fill=stroke_color)
    draw.text((x_pos, y_pos), text, font=font, fill="white")

def process_sticker(input_path, output_path, text):
    img = Image.open(input_path).convert("RGBA")
    img = img.resize((512, 512), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Montserrat-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
        
    lines = text.split("\\n")
    y_start = 512 - 30 - (len(lines) * 45)
    for i, line in enumerate(lines):
        draw_text(draw, line.strip(), font, 512, y_start + (i * 45))
    img.save(output_path, format="PNG")

# --- EXECUTE ---
raw_img = "raw_promo_pill.png"
final_img = "final_promo_pill.png"

if generate_image_vertex(prompt, raw_img):
    print("Image generated successfully. Adding text...")
    process_sticker(raw_img, final_img, text)
    
    print("Sending to Telegram bot...")
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN_SEND}/sendPhoto"
    with open(final_img, 'rb') as f:
        res = requests.post(send_url, data={'chat_id': USER_ID}, files={'photo': f})
        print(res.json())
else:
    print("Failed to generate.")
