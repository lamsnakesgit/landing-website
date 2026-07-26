import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("OPENcline_bot_old").strip()
USER_ID = "450206471"
PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

images_to_process = [
    {
        "in_path": "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_approved_1780946517596.png",
        "top_text": "СОГЛАСОВАНО",
        "bottom_text": "",
        "emoji": "✅"
    },
    {
        "in_path": "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_revisions_1780946528809.png",
        "top_text": "ЕЩЁ ПРАВОЧКА",
        "bottom_text": "",
        "emoji": "🫠"
    },
    {
        "in_path": "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_money_1780946538175.png",
        "top_text": "ГДЕ ДЕНЬГИ?",
        "bottom_text": "",
        "emoji": "💸"
    },
    {
        "in_path": "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_fire_1780946549025.png",
        "top_text": "",
        "bottom_text": "",
        "emoji": "🔥"
    }
]

def draw_text_with_outline(draw, x, y, text, font, fill_color):
    outline_color = (0, 0, 0, 255)
    thickness = 3
    for dx in [-thickness, 0, thickness]:
        for dy in [-thickness, 0, thickness]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def process_and_upload():
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    for item in images_to_process:
        print(f"Processing {item['in_path']}")
        out_path = "temp_sticker.png"
        
        with Image.open(item['in_path']) as img:
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                
            draw = ImageDraw.Draw(img)
            try:
                font_top = ImageFont.truetype("Montserrat-Bold.ttf", 40)
            except:
                font_top = ImageFont.load_default()
                
            if item['top_text']:
                bbox_c = draw.textbbox((0, 0), item['top_text'], font=font_top)
                cw = bbox_c[2] - bbox_c[0]
                cx = (512 - cw) / 2
                cy = 20
                draw_text_with_outline(draw, cx, cy, item['top_text'], font_top, (255, 255, 0, 255))
                
            img.save(out_path, "PNG")
            
        print("Uploading...")
        with open(out_path, 'rb') as f:
            resp = requests.post(
                f"{base_url}/uploadStickerFile",
                data={'user_id': USER_ID, 'sticker_format': 'static'},
                files={'sticker': f}
            )
            res_json = resp.json()
            if not res_json.get('ok'):
                print(f"Failed to upload: {res_json}")
                continue
            file_id = res_json['result']['file_id']
            
        print("Adding to set...")
        resp = requests.post(
            f"{base_url}/addStickerToSet",
            data={
                'user_id': USER_ID,
                'name': PACK_NAME,
                'sticker': json.dumps({"sticker": file_id, "emoji_list": [item['emoji']]})
            }
        )
        print(resp.json())

if __name__ == "__main__":
    process_and_upload()
