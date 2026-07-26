import os
import requests
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import google.auth
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIGURATION ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"
BOT_TOKEN_UPLOAD = os.getenv("OPENcline_bot_old").strip()
BOT_TOKEN_SEND = os.getenv("TG_REALSTATE_SMM_BOT").strip()
USER_ID = "450206471"

# --- 2. THE 8 CINEMATIC PROMPTS ---
base_char = "A cinematic high-quality rendering. A slightly dark-skinned young woman, wearing stylish glasses and a prominent ring on her RIGHT INDEX FINGER."

stickers_data = [
    {
        "id": "cine_poke",
        "prompt": f"{base_char} She is wearing a heavy space suit like in the movie Alien. She is standing in a dark, atmospheric sci-fi spaceship corridor, carefully poking a glowing alien cocoon (resembling a chat bubble) with a long futuristic staff. Expression is hope and desperation.",
        "text": "ПИКНИ, ЕСЛИ ЖИВОЙ 🥲"
    },
    {
        "id": "cine_hourglass",
        "prompt": f"{base_char} Cinematic mafia style like The Godfather. She is sitting in a dark, luxurious office wearing a tailored mafia suit, looking with deep disappointment at a giant hourglass on her desk. Inside the hourglass, glowing gold coins are falling instead of sand.",
        "text": "А МЫ ВЕДЬ МОГЛИ УЖЕ ЗАПУСТИТЬСЯ... ⏳"
    },
    {
        "id": "cine_lotus",
        "prompt": f"{base_char} Cinematic adventure style like Tomb Raider. She is sitting in a lotus meditation pose inside an ancient, dark jungle temple. She has literally turned into stone and is covered in ancient moss, vines, and dust, but she is still holding a glowing futuristic laptop showing an invoice.",
        "text": "Я ЖДУ ОПЛАТУ... И Я БЕССМЕРТНА 🧘‍♀️"
    },
    {
        "id": "cine_matrix_scroll",
        "prompt": f"{base_char} Cinematic cyberpunk style like The Matrix. She is wearing a black trench coat and dodging bullets in extreme slow motion backward bend (bullet time). The bullets flying past her have glowing red letters on them. Dramatic green matrix lighting.",
        "text": "ЕЩЁ ОДНА МАЛЕНЬКАЯ ПРАВОЧКА 📜"
    },
    {
        "id": "cine_magic_ai",
        "prompt": f"{base_char} Cinematic epic fantasy style like Harry Potter or LOTR. She is wearing an epic dark wizard robe on a mountain cliff during a thunderstorm. She slams a glowing magic staff into the ground, creating a massive magical shockwave made of green binary code.",
        "text": "ЩА НЕЙРОСЕТЬ ВСЁ ПОШАМАНЯТ 🤖✨"
    },
    {
        "id": "cine_pirate_budget",
        "prompt": f"{base_char} Cinematic pirate movie style. She is dressed as an epic pirate captain inside a dark treasure cave. She is opening a massive, ancient wooden treasure chest, but looking inside with extreme skepticism because at the very bottom sits only one tiny, rusty microscopic coin.",
        "text": "И ЭТО ВЕСЬ БЮДЖЕТ?! 🔍"
    },
    {
        "id": "cine_explosion",
        "prompt": f"{base_char} Cinematic action movie style like Iron Man. She is walking away in slow motion directly towards the camera, wearing cool sunglasses. Behind her is a colossal, fiery explosion made of servers, automation gears, and money. She is not looking back at the explosion.",
        "text": "ЩА ПОКАЖУ, КАК ДЕЛАЮТ ПРОФИ 💥"
    },
    {
        "id": "cine_dune_rocket",
        "prompt": f"{base_char} Cinematic sci-fi desert style like Dune. She is epicly riding a massive, terrifying Sandworm through the desert, but the sandworm looks like a giant green stock market chart going straight up into the sky. Confident and victorious.",
        "text": "ROI УЛЕТЕЛ В КОСМОС 🚀"
    }
]

# --- 3. VERTEX AI AUTHENTICATION ---
print("Authenticating with Vertex AI...")
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

# --- 4. PROCESSING FUNCTIONS ---
def draw_text(draw, text, font, width, y_pos):
    # Same drawing logic as before
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x_pos = (width - text_w) / 2
    
    # Text stroke/outline
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
        font = ImageFont.truetype("Montserrat-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()
        
    lines = text.split("\\n") if "\\n" in text else [text]
    if len(lines) == 1 and len(text) > 20:
        words = text.split()
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        
    y_start = 512 - 20 - (len(lines) * 40)
    for i, line in enumerate(lines):
        draw_text(draw, line.strip(), font, 512, y_start + (i * 40))
        
    img.save(output_path, format="PNG")

# --- 5. EXECUTION PIPELINE ---
generated_files = []

for item in stickers_data:
    raw_img = f"raw_{item['id']}.png"
    final_img = f"final_{item['id']}.png"
    
    if generate_image_vertex(item['prompt'], raw_img):
        process_sticker(raw_img, final_img, item['text'])
        generated_files.append(final_img)

# Upload and Send
print("Uploading to Telegram...")
upload_url = f"https://api.telegram.org/bot{BOT_TOKEN_UPLOAD}/addStickerToSet"
send_url = f"https://api.telegram.org/bot{BOT_TOKEN_SEND}/sendPhoto"

for img_path in generated_files:
    # 1. Add to sticker pack
    with open(img_path, 'rb') as f:
        res = requests.post(upload_url, data={
            'user_id': USER_ID,
            'name': 'nnsvt_pack_1780750023_by_OpenCline_bot',
            'emojis': '🎬'
        }, files={'png_sticker': f})
        print(f"Added {img_path}: {res.json()}")
        
    # 2. Send to Antigravity bot
    with open(img_path, 'rb') as f:
        requests.post(send_url, data={'chat_id': USER_ID}, files={'photo': f})
        
print("All done!")
