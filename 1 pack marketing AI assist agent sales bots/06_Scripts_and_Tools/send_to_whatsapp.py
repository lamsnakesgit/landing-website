import os
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("EVOLUTION_BASE_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = os.getenv("EVOLUTION_INSTANCE").strip()
PHONE = "77771269911"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

# 1. Send Voice Message
voice_file = "summary_voice.mp3"
if os.path.exists(voice_file):
    print(f"Sending voice message {voice_file}...")
    with open(voice_file, "rb") as f:
        b64_audio = base64.b64encode(f.read()).decode("utf-8")
    
    url_audio = f"{BASE_URL}/message/sendWhatsAppAudio/{INSTANCE}"
    payload_audio = {
        "number": PHONE,
        "audio": f"data:audio/mp3;base64,{b64_audio}",
        "delay": 1200,
        "encoding": True
    }
    res = requests.post(url_audio, json=payload_audio, headers=headers)
    print("Voice response:", res.status_code, res.text)
    time.sleep(2)

# 2. Send Stickers
stickers = [
    "final_cine_poke.png",
    "final_cine_hourglass.png",
    "final_cine_lotus.png",
    "final_cine_matrix_scroll.png",
    "final_cine_explosion.png",
    "final_promo_pill.png"
]

url_sticker = f"{BASE_URL}/message/sendSticker/{INSTANCE}"

for sticker_file in stickers:
    if os.path.exists(sticker_file):
        print(f"Sending sticker {sticker_file}...")
        with open(sticker_file, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        
        payload_sticker = {
            "number": PHONE,
            "sticker": f"data:image/png;base64,{b64_img}",
            "delay": 1200
        }
        res = requests.post(url_sticker, json=payload_sticker, headers=headers)
        print(f"Sticker {sticker_file} response:", res.status_code, res.text)
        time.sleep(1)
