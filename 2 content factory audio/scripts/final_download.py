import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")
FILE_URI = "https://generativelanguage.googleapis.com/v1beta/files/nyzw2l5pdzl3:download?alt=media"
OUTPUT_PATH = Path("outputs/veo_avatar_final.mp4")

def download_video():
    print(f"📡 Попытка скачать видео напрямую...")
    # Используем заголовок для авторизации
    headers = {"x-goog-api-key": API_KEY}
    
    try:
        response = requests.get(FILE_URI, headers=headers)
        if response.status_code == 200:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_PATH.write_bytes(response.content)
            print(f"🎉 УСПЕХ! Видео сохранено: {OUTPUT_PATH} ({len(response.content)} байт)")
        else:
            print(f"❌ Ошибка: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    download_video()
