import os, requests, time
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

files_to_upload = [
    ("sticker_tongue.png", ["👅", "💰"]),
    ("dozhim_skeleton.png", ["💀", "⏳"]),
    ("dozhim_search.png", ["🔦", "👀"])
]

def get_bot_username():
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe").json()
    return resp['result']['username']

def upload_file(path):
    print(f"Uploading {path}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
    with open(path, "rb") as f:
        resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files={'sticker': f})
    res = resp.json()
    if res.get('ok'):
        return res['result']['file_id']
    else:
        print(f"Upload failed for {path}:", res)
        return None

def create_pack(name, title, sticker_type, stickers):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createNewStickerSet"
    payload = {
        'user_id': CHAT_ID,
        'name': name,
        'title': title,
        'stickers': stickers,
        'sticker_format': 'static',
        'sticker_type': sticker_type
    }
    resp = requests.post(url, json=payload).json()
    print(f"Create pack {name}: {resp}")
    return resp.get('ok')

if __name__ == "__main__":
    bot_username = get_bot_username()
    ts = int(time.time())
    
    # Upload all files first
    uploaded_stickers = []
    for file_path, emojis in files_to_upload:
        if os.path.exists(file_path):
            fid = upload_file(file_path)
            if fid:
                uploaded_stickers.append({"sticker": fid, "emoji_list": emojis})
    
    if not uploaded_stickers:
        print("No files uploaded.")
        exit()

    # Create Regular Pack
    reg_name = f"nnsvt_sales_{ts}_by_{bot_username}"
    if create_pack(reg_name, "NNSVT Sales AI", "regular", uploaded_stickers):
        link_reg = f"https://t.me/addstickers/{reg_name}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"🔥 Готово! Твой НОВЫЙ основной стикерпак (привязан к Антигравити):\n{link_reg}"})
        
    # Create Emoji Pack
    emoji_name = f"nnsvt_emoji_{ts}_by_{bot_username}"
    if create_pack(emoji_name, "NNSVT Emojis AI", "custom_emoji", uploaded_stickers):
        link_emoji = f"https://t.me/addstickers/{emoji_name}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"⚡️ А вот твой ЭМОДЗИ-пак (можно вставлять в текст):\n{link_emoji}"})
