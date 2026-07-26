import os
import requests
import json
import time
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
USER_ID = os.getenv("TG_REALSTATE_SMM_CHAT_ID")
PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

input_dir = "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0"
output_dir = "stickers_watermarked_batch3"
os.makedirs(output_dir, exist_ok=True)

situations = [
    {"prefix": "11_think", "emoji": "👻"},
    {"prefix": "12_lowballer", "emoji": "📉"},
    {"prefix": "13_dinosaur", "emoji": "🦖"},
    {"prefix": "14_midnight_edits", "emoji": "🦉"},
    {"prefix": "15_trash_leads", "emoji": "🗑️"},
    {"prefix": "16_rug_pull", "emoji": "💔"},
    {"prefix": "17_zen_mode", "emoji": "🧘‍♂️"}
]

def add_watermark(image_path, output_path, text="@nnsvt"):
    try:
        with Image.open(image_path) as img:
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("Montserrat-Bold.ttf", 36)
            except:
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (512 - text_w) / 2
            y = 512 - text_h - 20 
            
            shadow_color = (0, 0, 0, 180)
            outline_thickness = 2
            for dx in [-outline_thickness, 0, outline_thickness]:
                for dy in [-outline_thickness, 0, outline_thickness]:
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
                    
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            img.save(output_path, "PNG")
            return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def upload_sticker(output_path, emoji):
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    print(f"Uploading {output_path} to Telegram...")
    with open(output_path, 'rb') as f:
        resp = requests.post(
            f"{base_url}/uploadStickerFile",
            data={'user_id': USER_ID, 'sticker_format': 'static'},
            files={'sticker': f}
        )
        res_json = resp.json()
        if not res_json.get('ok'):
            print(f"Failed to upload file {output_path}: {res_json}")
            return False
            
        file_id = res_json['result']['file_id']
        
    print(f"Adding to sticker set {PACK_NAME}...")
    resp = requests.post(
        f"{base_url}/addStickerToSet",
        data={
            'user_id': USER_ID,
            'name': PACK_NAME,
            'sticker': json.dumps({"sticker": file_id, "emoji_list": [emoji]})
        }
    )
    if resp.json().get('ok'):
        print(f"✅ Successfully added to set")
        return True
    else:
        print(f"❌ Failed to add sticker to set: {resp.json()}")
        return False

for item in situations:
    # Find matching file in input_dir
    matching = [f for f in os.listdir(input_dir) if f.startswith(item["prefix"]) and f.endswith(".png")]
    if matching:
        in_path = os.path.join(input_dir, matching[0])
        out_path = os.path.join(output_dir, f"{item['prefix']}.png")
        if add_watermark(in_path, out_path):
            upload_sticker(out_path, item["emoji"])
            time.sleep(1)
    else:
        print(f"Source file not found for {item['prefix']}")
