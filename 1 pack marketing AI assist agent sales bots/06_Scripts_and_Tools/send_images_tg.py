import os
import requests
import time

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

files = ["wednesday", "mermaid", "brainrot", "sprunki", "house", "city", "coins", "kpop_demon"]

for name in files:
    filepath = f"маркет_мобил_приложений/avatarworld/generated_bg/out_{name}.png"
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            files_req = {'photo': f}
            data = {'chat_id': CHAT_ID, 'caption': f"Avatar World Background: {name}"}
            resp = requests.post(API_URL, data=data, files=files_req)
            print(f"Sent {filepath}: {resp.status_code}")
        time.sleep(1)
    else:
        print(f"{filepath} not found")
