import os
import requests
import time
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load env variables
load_dotenv()

AIHUBMIX_API_KEY = os.getenv("AIHUBMIX_API_KEY")
BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
USER_ID = os.getenv("TG_REALSTATE_SMM_CHAT_ID")
# Pack name from previous logs
PACK_NAME = "ai_sales_pack_1780748912_by_OpenCline_bot"

prompts = [
    {
        "name": "01_cold_call",
        "emoji": "🥶",
        "prompt": "A sleek, modern 3D icon of an AI robot holding a telephone, but the robot is completely frozen, covered in ice and icicles, with X_X eyes. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "name": "02_deal_closed",
        "emoji": "😎",
        "prompt": "A sleek, modern 3D icon of a cool AI robot wearing thug life sunglasses, making it rain dollar bills, with a briefcase full of money next to it. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "name": "03_waiting_payment",
        "emoji": "⏳",
        "prompt": "A sleek, modern 3D icon of an AI robot sitting at a desk looking at a wristwatch, covered in cobwebs, with a sign saying 'Waiting for Invoice'. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "name": "04_meeting_overload",
        "emoji": "🤯",
        "prompt": "A sleek, modern 3D icon of an exhausted AI robot with red spinning eyes, drowning in a chaotic pile of floating Zoom video call windows, calendars, and emails. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "name": "05_bot_works_24_7",
        "emoji": "🦾",
        "prompt": "A sleek, modern 3D icon of an AI robot with four arms, holding laptops and phones, running cheerfully on a hamster wheel while drinking motor oil. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    },
    {
        "name": "06_client_edits",
        "emoji": "🤬",
        "prompt": "A sleek, modern 3D icon of a stressed AI robot holding a document titled 'FINAL_v2_real.pdf', with electrical sparks flying from its head and a twitching eye. Clean solid white background. High quality, vivid colors, suitable for a telegram sticker."
    }
]

def generate_image_aihubmix(prompt_text):
    print(f"Generating image for prompt: {prompt_text[:50]}...")
    url = "https://api.aihubmix.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {AIHUBMIX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt_text,
        "n": 1,
        "size": "1024x1024"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return None

def process_and_resize(image_url, filename):
    print(f"Downloading and resizing to 512x512: {filename}...")
    response = requests.get(image_url)
    with Image.open(BytesIO(response.content)) as img:
        # Resize to exactly 512x512
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        # Add alpha channel if it doesn't have one
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.save(filename, "PNG")
    print(f"Saved: {filename}")

def add_sticker_to_pack(bot_token, user_id, pack_name, sticker_path, emojis):
    print(f"Uploading {sticker_path} to Telegram...")
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    with open(sticker_path, 'rb') as f:
        response = requests.post(
            f"{base_url}/uploadStickerFile",
            data={'user_id': user_id, 'sticker_format': 'static'},
            files={'sticker': f}
        )
    
    res = response.json()
    if not res.get('ok'):
        print(f"Upload error: {res}")
        return False
        
    file_id = res['result']['file_id']
    
    print(f"Adding to pack {pack_name}...")
    # Escape quotes properly
    stickers_data = '[{"sticker": "' + file_id + '", "emoji_list": ["' + '", "'.join(list(emojis)) + '"]}]'
    
    # Actually add the sticker to the existing set
    # Oh wait, addStickerToSet requires sending a single sticker object.
    # The API for addStickerToSet is slightly different in modern Telegram Bot API.
    # It takes a `sticker` object directly, not an array.
    # Wait, as of Bot API 6.6+, addStickerToSet takes `sticker` parameter as JSON object.
    
    sticker_obj = '{"sticker": "' + file_id + '", "emoji_list": ["' + '", "'.join(list(emojis)) + '"]}'
    
    response = requests.post(
        f"{base_url}/addStickerToSet",
        data={
            'user_id': user_id,
            'name': pack_name,
            'sticker': sticker_obj
        }
    )
    
    res2 = response.json()
    if res2.get('ok'):
        print(f"✅ Added {sticker_path} successfully!")
        return True
    else:
        print(f"❌ Add error: {res2}")
        return False

def main():
    if not AIHUBMIX_API_KEY:
        print("Missing AIHUBMIX_API_KEY")
        return
        
    os.makedirs("stickers", exist_ok=True)
    
    for item in prompts:
        # 1. Generate
        img_url = generate_image_aihubmix(item["prompt"])
        if not img_url:
            continue
            
        # 2. Process
        filename = f"stickers/{item['name']}.png"
        process_and_resize(img_url, filename)
        
        # 3. Upload
        add_sticker_to_pack(BOT_TOKEN, USER_ID, PACK_NAME, filename, item["emoji"])
        
        print("-" * 30)
        time.sleep(1)
        
    print(f"\nAll done! Check your sticker pack: https://t.me/addstickers/{PACK_NAME}")

if __name__ == "__main__":
    main()
