import os, requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

with open("sticker_tongue.png", "rb") as f:
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        data={'chat_id': CHAT_ID, 'caption': 'Лови прозрачный PNG! Перешли его боту @Stickers, чтобы добавить в свой старый пак.'},
        files={'document': f}
    )
print(resp.json())
