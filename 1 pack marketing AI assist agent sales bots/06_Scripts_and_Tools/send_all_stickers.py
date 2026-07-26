import requests
import os
import glob
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("OPENcline_bot_old").strip()
USER_ID = "450206471"

files_to_send = [
    "final_cine_poke.png",
    "final_cine_hourglass.png",
    "final_cine_lotus.png",
    "final_cine_matrix_scroll.png",
    "final_cine_explosion.png",
    "final_promo_pill.png"
]

send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

for file_name in files_to_send:
    if os.path.exists(file_name):
        with open(file_name, 'rb') as f:
            print(f"Sending {file_name}...")
            res = requests.post(send_url, data={'chat_id': USER_ID}, files={'document': f})
            print(res.json())
        time.sleep(1)
    else:
        print(f"File {file_name} not found.")
