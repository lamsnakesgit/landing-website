import requests
import sys

TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
FILE_PATH = "tts_report.mp3"

try:
    url = f"https://api.telegram.org/bot{TOKEN}/sendVoice"
    with open(FILE_PATH, 'rb') as f:
        files = {'voice': f}
        data = {'chat_id': CHAT_ID}
        response = requests.post(url, files=files, data=data)
    print("Voice sent:", response.json())
except Exception as e:
    print("Error:", e)
