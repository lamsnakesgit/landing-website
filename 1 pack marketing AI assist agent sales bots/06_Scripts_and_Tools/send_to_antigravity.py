import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN").strip()
USER_ID = "888005446"

files_to_send = [
    "summary_voice.mp3",
    "final_cine_poke.png",
    "final_cine_hourglass.png",
    "final_cine_lotus.png",
    "final_cine_matrix_scroll.png",
    "final_cine_explosion.png",
    "final_promo_pill.png",
    "reference_links.md"
]

for file_name in files_to_send:
    if os.path.exists(file_name):
        print(f"Sending {file_name} to Antigravity bot...")
        if file_name.endswith(".mp3"):
            res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio", 
                                data={'chat_id': USER_ID}, 
                                files={'audio': open(file_name, "rb")})
        else:
            res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                                data={'chat_id': USER_ID}, 
                                files={'document': open(file_name, "rb")})
        print(f"Result for {file_name}:", res.json().get('ok'))
        time.sleep(1)
