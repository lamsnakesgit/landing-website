import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("CONTENT_FACTORY_BOT").strip()
USER_ID = "888005446"

# Send Audio
print("Sending audio to Content Factory Bot...")
res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio", 
                    data={'chat_id': USER_ID}, 
                    files={'audio': open("summary_voice.mp3", "rb")})
print("Audio result:", res.json().get('ok'))
time.sleep(1)

# Send promo sticker
print("Sending promo sticker to Content Factory Bot...")
res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                    data={'chat_id': USER_ID}, 
                    files={'document': open("final_promo_pill.png", "rb")})
print("Sticker result:", res.json().get('ok'))
