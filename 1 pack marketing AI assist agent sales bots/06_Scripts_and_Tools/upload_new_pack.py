import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
USER_ID = os.getenv("TG_REALSTATE_SMM_CHAT_ID")

stickers_dir = "stickers_watermarked"

# Define order and emojis
sticker_map = [
    ("01_cold_call.png", "🥶"),
    ("02_deal_closed.png", "😎"),
    ("03_waiting_payment.png", "⏳"),
    ("04_meeting_overload.png", "🤯"),
    ("05_bot_works_24_7.png", "🦾"),
    ("06_client_edits.png", "🤬")
]

def upload_and_create_pack():
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    bot_info = requests.get(f"{base_url}/getMe").json()
    bot_username = bot_info['result']['username']
    
    pack_name = f"nnsvt_pack_{int(time.time())}_by_{bot_username}"
    pack_title = "@nnsvt Sales Agents"
    
    print("Uploading stickers to Telegram servers...")
    
    uploaded_stickers = []
    
    for filename, emoji in sticker_map:
        path = os.path.join(stickers_dir, filename)
        print(f"Uploading {filename}...")
        with open(path, 'rb') as f:
            resp = requests.post(
                f"{base_url}/uploadStickerFile",
                data={'user_id': USER_ID, 'sticker_format': 'static'},
                files={'sticker': f}
            )
            res_json = resp.json()
            if not res_json.get('ok'):
                print(f"Failed to upload {filename}: {res_json}")
                continue
            
            file_id = res_json['result']['file_id']
            uploaded_stickers.append({"sticker": file_id, "emoji_list": [emoji]})
            time.sleep(0.5)
            
    if not uploaded_stickers:
        print("No stickers were uploaded.")
        return
        
    print(f"Creating new sticker pack '{pack_title}'...")
    import json
    stickers_data = json.dumps(uploaded_stickers)
    
    resp = requests.post(
        f"{base_url}/createNewStickerSet",
        data={
            'user_id': USER_ID,
            'name': pack_name,
            'title': pack_title,
            'stickers': stickers_data,
            'sticker_format': 'static'
        }
    )
    
    res = resp.json()
    if res.get('ok'):
        print(f"\n✅ Pack created successfully!")
        print(f"👉 Link: https://t.me/addstickers/{pack_name}")
    else:
        print(f"\n❌ Error creating pack: {res}")

if __name__ == "__main__":
    upload_and_create_pack()
