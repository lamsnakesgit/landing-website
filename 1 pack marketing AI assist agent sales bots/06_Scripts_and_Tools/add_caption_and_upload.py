import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
USER_ID = os.getenv("TG_REALSTATE_SMM_CHAT_ID")
PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

in_path = "concept_duo_girl_ai.png"
out_path = "concept_sticker_with_text.png"
caption = "СОГЛАСОВАНО!"
watermark = "@nnsvt"

def process_image():
    with Image.open(in_path) as img:
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        draw = ImageDraw.Draw(img)
        try:
            font_caption = ImageFont.truetype("Montserrat-Bold.ttf", 54)
            font_watermark = ImageFont.truetype("Montserrat-Bold.ttf", 30)
        except:
            font_caption = ImageFont.load_default()
            font_watermark = ImageFont.load_default()
            
        # Draw Caption (Top)
        bbox_c = draw.textbbox((0, 0), caption, font=font_caption)
        cw = bbox_c[2] - bbox_c[0]
        cx = (512 - cw) / 2
        cy = 20
        
        # Draw Watermark (Bottom)
        bbox_w = draw.textbbox((0, 0), watermark, font=font_watermark)
        ww = bbox_w[2] - bbox_w[0]
        wh = bbox_w[3] - bbox_w[1]
        wx = (512 - ww) / 2
        wy = 512 - wh - 20
        
        # Function for outlined text
        def draw_text_with_outline(x, y, text, font, fill_color):
            outline_color = (0, 0, 0, 255)
            thickness = 3
            for dx in [-thickness, 0, thickness]:
                for dy in [-thickness, 0, thickness]:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
            draw.text((x, y), text, font=font, fill=fill_color)
            
        draw_text_with_outline(cx, cy, caption, font_caption, (255, 255, 0, 255)) # Yellow text
        draw_text_with_outline(wx, wy, watermark, font_watermark, (255, 255, 255, 255)) # White watermark
        
        img.save(out_path, "PNG")
        return True

def upload_to_tg():
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    print("Uploading sticker...")
    with open(out_path, 'rb') as f:
        resp = requests.post(
            f"{base_url}/uploadStickerFile",
            data={'user_id': USER_ID, 'sticker_format': 'static'},
            files={'sticker': f}
        )
        res_json = resp.json()
        if not res_json.get('ok'):
            print(f"Failed to upload: {res_json}")
            return
        file_id = res_json['result']['file_id']
        
    print("Adding to set...")
    resp = requests.post(
        f"{base_url}/addStickerToSet",
        data={
            'user_id': USER_ID,
            'name': PACK_NAME,
            'sticker': json.dumps({"sticker": file_id, "emoji_list": ["✅"]})
        }
    )
    print(resp.json())

if process_image():
    upload_to_tg()
