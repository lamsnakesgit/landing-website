import os, requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
PACK_NAME = "nns_e_1781340644_by_test14fbot"

pack = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={PACK_NAME}").json()
print("PACK STATUS:", pack.get("ok"))
if pack.get("ok"):
    stickers = pack['result']['stickers']
    print(f"Stickers count: {len(stickers)}")
    if len(stickers) > 0:
        first_sticker_id = stickers[0]['file_id']
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={'chat_id': CHAT_ID, 'text': f"Смотри, отправляю эмодзи программно из пака: {PACK_NAME}"}
        )
        print("Message sent:", resp.json())
        
        resp2 = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker",
            data={'chat_id': CHAT_ID, 'sticker': first_sticker_id}
        )
        print("Sticker sent:", resp2.json())
else:
    print(pack)
