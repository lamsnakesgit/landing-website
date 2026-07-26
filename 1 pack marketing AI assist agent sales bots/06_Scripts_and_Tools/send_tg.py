import requests
import sys

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
PHOTO_PATH = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/nano_final_edit_date.jpg"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

def send_photo():
    with open(PHOTO_PATH, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": CHAT_ID, "caption": "Афиша готова! 🚀"}
        print("Sending photo to TG...")
        response = requests.post(URL, data=data, files=files)
        print(response.json())

if __name__ == "__main__":
    send_photo()
