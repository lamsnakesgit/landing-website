import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("CONTENT_FACTORY_BOT").strip()
USER_ID = "450206471"

send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
with open("final_promo_pill.png", 'rb') as f:
    res = requests.post(send_url, data={'chat_id': USER_ID}, files={'photo': f})
    print(res.json())
