import os, requests, time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
OLD_PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

new_stickers_files = [
    ("sticker_tongue.png", ["👅", "💰"]),
    ("dozhim_skeleton.png", ["💀", "⏳"]),
    ("dozhim_search.png", ["🔦", "👀"])
]

def get_bot_username():
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10).json()
    return resp['result']['username']

def download_file(file_id):
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
    if resp.get('ok'):
        file_path = resp['result']['file_path']
        d_resp = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}", timeout=20)
        return d_resp.content
    return None

def upload_file(content):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
    files = {'sticker': ('sticker.png', content, 'image/png')}
    resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files=files, timeout=20)
    res = resp.json()
    if res.get('ok'):
        return res['result']['file_id']
    else:
        print("Upload failed:", res, flush=True)
    return None

def create_pack(name, title, sticker_type, stickers):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createNewStickerSet"
    first_batch = stickers[:50]
    payload = {
        'user_id': CHAT_ID,
        'name': name,
        'title': title,
        'stickers': first_batch,
        'sticker_format': 'static',
        'sticker_type': sticker_type
    }
    resp = requests.post(url, json=payload, timeout=20).json()
    print(f"Create pack {name}: {resp}", flush=True)
    if resp.get('ok') and len(stickers) > 50:
        for st in stickers[50:]:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/addStickerToSet", json={
                'user_id': CHAT_ID, 'name': name, 'sticker': st
            }, timeout=20)
    return resp.get('ok')

if __name__ == "__main__":
    bot_username = get_bot_username()
    ts = int(time.time())
    
    old_pack_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={OLD_PACK_NAME}").json()
    old_stickers = []
    if old_pack_resp.get('ok'):
        old_stickers = old_pack_resp['result']['stickers']
    
    reg_stickers = []
    emoji_stickers = []
    
    print(f"Found {len(old_stickers)} old stickers.", flush=True)
    
    for i, st in enumerate(old_stickers):
        fid = st['file_id']
        emoji = st['emoji']
        print(f"Processing old sticker {i+1}/{len(old_stickers)}...", flush=True)
        content = download_file(fid)
        if content:
            new_fid = upload_file(content)
            if new_fid:
                reg_stickers.append({"sticker": new_fid, "emoji_list": [emoji]})
            img = Image.open(BytesIO(content)).convert("RGBA")
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            out = BytesIO()
            img.save(out, format="PNG")
            out.seek(0)
            emo_fid = upload_file(out.read())
            if emo_fid:
                emoji_stickers.append({"sticker": emo_fid, "emoji_list": [emoji]})
        time.sleep(0.5)
        
    for file_path, emojis in new_stickers_files:
        if os.path.exists(file_path):
            print(f"Processing new sticker {file_path}...", flush=True)
            with open(file_path, "rb") as f:
                content = f.read()
            fid_reg = upload_file(content)
            if fid_reg:
                reg_stickers.append({"sticker": fid_reg, "emoji_list": emojis})
            img = Image.open(BytesIO(content)).convert("RGBA")
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            out = BytesIO()
            img.save(out, format="PNG")
            out.seek(0)
            fid_emoji = upload_file(out.read())
            if fid_emoji:
                emoji_stickers.append({"sticker": fid_emoji, "emoji_list": emojis})

    title = "@vacancydigitalaize | @unleash_assistant_bo"
    
    if reg_stickers:
        reg_name = f"nns_r_{ts}_by_{bot_username}"
        if create_pack(reg_name, title, "regular", reg_stickers):
            link = f"https://t.me/addstickers/{reg_name}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"✅ ВСЕ стикеры (старые + 3 новых) перенесены в один пак с коротким названием:\n{link}"})
            
    if emoji_stickers:
        emoji_name = f"nns_e_{ts}_by_{bot_username}"
        if create_pack(emoji_name, title, "custom_emoji", emoji_stickers):
            link = f"https://t.me/addstickers/{emoji_name}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"⚡️ А вот ЭМОДЗИ-пак со всеми картинками:\n{link}"})
