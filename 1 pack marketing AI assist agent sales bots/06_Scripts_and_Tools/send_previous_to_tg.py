import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Using the other bot just in case
BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT").strip()
USER_ID = "450206471"

images = [
    "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_approved_1780946517596.png",
    "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_revisions_1780946528809.png",
    "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_money_1780946538175.png",
    "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/generic_fire_1780946549025.png"
]

def send_to_tg():
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    requests.post(f"{base_url}/sendMessage", json={
        "chat_id": USER_ID,
        "text": "Отправляю дубль через TG_REALSTATE_SMM_BOT! Вот 4 универсальных стикера:"
    })
    
    for img_path in images:
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                requests.post(
                    f"{base_url}/sendPhoto",
                    data={'chat_id': USER_ID},
                    files={'photo': f}
                )

if __name__ == "__main__":
    send_to_tg()
