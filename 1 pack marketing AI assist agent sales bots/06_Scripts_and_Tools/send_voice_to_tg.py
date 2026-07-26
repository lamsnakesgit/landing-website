import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("OPENcline_bot_old").strip()
USER_ID = "450206471"

file_name = "summary_voice.mp3"

send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"

if os.path.exists(file_name):
    with open(file_name, 'rb') as f:
        print(f"Sending {file_name} to Telegram...")
        res = requests.post(send_url, data={'chat_id': USER_ID}, files={'audio': f})
        print(res.json())
else:
    print("Voice file not found!")
