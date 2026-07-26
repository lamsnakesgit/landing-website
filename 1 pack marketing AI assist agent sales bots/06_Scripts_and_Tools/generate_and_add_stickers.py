import os
import requests
import json
import time
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
USER_ID = os.getenv("TG_REALSTATE_SMM_CHAT_ID")
PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

output_dir = "stickers_watermarked_batch2"
os.makedirs(output_dir, exist_ok=True)

# Prompts for the 8 situations
situations = [
    {
        "filename": "11_think.png",
        "emoji": "👻",
        "prompt": "A sleek, modern 3D icon of a sad AI robot looking at a smartphone screen that says 'Read 12:00', with a small ghost floating nearby. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "12_lowballer.png",
        "emoji": "📉",
        "prompt": "A sleek, modern 3D icon of a shocked AI robot looking at a tiny single copper coin, holding its head in disbelief. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "13_dinosaur.png",
        "emoji": "🦖",
        "prompt": "A sleek, modern 3D icon of an AI robot covered in yellow sticky notes, trying to type on a primitive stone keyboard. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "14_midnight_edits.png",
        "emoji": "🦉",
        "prompt": "A sleek, modern 3D icon of a tired AI robot in a nightcap, with huge dark circles under red eyes, drinking coffee directly from a pot, surrounded by floating voice message icons. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "15_trash_leads.png",
        "emoji": "🗑️",
        "prompt": "A sleek, modern 3D icon of an AI robot holding a tennis racket, batting away golden coins into a trash can. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "16_rug_pull.png",
        "emoji": "💔",
        "prompt": "A sleek, modern 3D icon of an AI robot reaching for a glowing 'PAY' button, but a giant cartoon anvil is falling to crush the button. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "17_zen_mode.png",
        "emoji": "🧘‍♂️",
        "prompt": "A sleek, modern 3D icon of an AI robot sitting in a zen lotus meditation pose, with floating laptops and gold coins orbiting around it. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "filename": "18_mission_impossible.png",
        "emoji": "🍏",
        "prompt": "A sleek, modern 3D icon of an AI robot trying to assemble a space shuttle using only sticks, blue duct tape, and glue. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    }
]

def generate_image_gemini(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"
    payload = {
      "instances": [{"prompt": prompt_text}],
      "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1",
        "outputOptions": {"mimeType": "image/png"}
      }
    }
    headers = {"Content-Type": "application/json"}
    print(f"Calling Gemini API for prompt: {prompt_text[:50]}...")
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Error from Gemini API: {resp.text}")
        return None
        
    data = resp.json()
    try:
        b64_data = data['predictions'][0]['bytesBase64Encoded']
        return base64.b64decode(b64_data)
    except Exception as e:
        print(f"Failed to parse Gemini response: {e}")
        return None

def process_and_watermark(image_bytes, output_path, text="@nnsvt"):
    try:
        img = Image.open(BytesIO(image_bytes))
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
        print(f"Error processing image: {e}")
        return False

def upload_sticker(filename, emoji):
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    path = os.path.join(output_dir, filename)
    print(f"Uploading {filename} to Telegram...")
    with open(path, 'rb') as f:
        resp = requests.post(
            f"{base_url}/uploadStickerFile",
            data={'user_id': USER_ID, 'sticker_format': 'static'},
            files={'sticker': f}
        )
        res_json = resp.json()
        if not res_json.get('ok'):
            print(f"Failed to upload file {filename}: {res_json}")
            return False
            
        file_id = res_json['result']['file_id']
        
    print(f"Adding {filename} to sticker set {PACK_NAME}...")
    resp = requests.post(
        f"{base_url}/addStickerToSet",
        data={
            'user_id': USER_ID,
            'name': PACK_NAME,
            'sticker': json.dumps({"sticker": file_id, "emoji_list": [emoji]})
        }
    )
    if resp.json().get('ok'):
        print(f"✅ Successfully added {filename}")
        return True
    else:
        print(f"❌ Failed to add sticker to set: {resp.json()}")
        return False

if __name__ == "__main__":
    for item in situations:
        print(f"\n--- Processing {item['filename']} ---")
        img_bytes = generate_image_gemini(item['prompt'])
        if img_bytes:
            out_path = os.path.join(output_dir, item['filename'])
            if process_and_watermark(img_bytes, out_path):
                upload_sticker(item['filename'], item['emoji'])
        time.sleep(1) # Rate limit protection
