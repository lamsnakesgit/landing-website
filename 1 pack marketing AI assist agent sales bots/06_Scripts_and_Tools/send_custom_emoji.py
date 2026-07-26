import os, requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
PACK_NAME = "nns_e_1781340644_by_test14fbot"

pack = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={PACK_NAME}").json()
if pack.get("ok"):
    stickers = pack['result']['stickers']
    if len(stickers) > 0:
        first_sticker_id = stickers[0]['custom_emoji_id']
        payload = {
            'chat_id': CHAT_ID,
            'text': "Вот твой эмодзи: X\nКликай прямо по нему!",
            'entities': [
                {
                    'type': 'custom_emoji',
                    'offset': 17,
                    'length': 1,
                    'custom_emoji_id': first_sticker_id
                }
            ]
        }
        resp = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
        print("Sent inline emoji:", resp.json())
