import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID_MAIN")
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

files = ["wednesday", "sprunki", "brainrot", "mermaid"]

for name in files:
    filepath = f"маркет_мобил_приложений/avatarworld/generated_bg/out_strict_{name}.png"
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            files_req = {'photo': f}
            data = {'chat_id': CHAT_ID, 'caption': f"Strict BG only: {name} (Square Icon)"}
            r = requests.post(URL, files=files_req, data=data)
            print(f"Sent {filepath}: {r.status_code}")
    else:
        print(f"File not found: {filepath}")
