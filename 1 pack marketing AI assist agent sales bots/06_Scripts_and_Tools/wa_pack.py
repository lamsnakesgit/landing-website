import os, requests, zipfile
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
OLD_PACK_NAME = "nnsvt_pack_1780750023_by_OpenCline_bot"

new_stickers_files = [
    "sticker_tongue.png",
    "dozhim_skeleton.png",
    "dozhim_search.png"
]

def download_file(file_id):
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}", timeout=10).json()
    if resp.get('ok'):
        file_path = resp['result']['file_path']
        d_resp = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}", timeout=20)
        return d_resp.content
    return None

def create_wa_pack():
    os.makedirs("wa_pack", exist_ok=True)
    
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': 'Начал сборку архива для WhatsApp. Скачиваю стикеры...'})
    
    # Get old stickers
    old_pack_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={OLD_PACK_NAME}").json()
    if old_pack_resp.get('ok'):
        for i, st in enumerate(old_pack_resp['result']['stickers']):
            content = download_file(st['file_id'])
            if content:
                img = Image.open(BytesIO(content)).convert("RGBA")
                img = img.resize((512, 512), Image.Resampling.LANCZOS)
                img.save(f"wa_pack/sticker_{i}.webp", "WEBP")
    
    # Process new stickers
    for i, path in enumerate(new_stickers_files):
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            img.save(f"wa_pack/new_sticker_{i}.webp", "WEBP")
            
    # Zip it up
    with zipfile.ZipFile("whatsapp_stickers.zip", "w") as zf:
        for root, dirs, files in os.walk("wa_pack"):
            for file in files:
                if file.endswith(".webp"):
                    zf.write(os.path.join(root, file), file)

    # Send ZIP
    with open("whatsapp_stickers.zip", "rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
            data={'chat_id': CHAT_ID, 'caption': '📦 Твои стикеры для WhatsApp (WebP 512x512). \n\nКак установить:\n1. Скачай этот архив на телефон и распакуй.\n2. Скачай бесплатное приложение типа "Sticker Maker" (есть в AppStore и Google Play).\n3. Нажми "Создать пак" и выбери все эти картинки. Готово!'}, 
            files={'document': f}
        )

if __name__ == "__main__":
    create_wa_pack()
