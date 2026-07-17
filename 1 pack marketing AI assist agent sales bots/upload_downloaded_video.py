import os
import requests
import sys
from dotenv import load_dotenv

# Отключаем буферизацию вывода
sys.stdout.reconfigure(line_buffering=True)

# Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv("MATON_API_KEY")
if not TOKEN:
    print("Ошибка: MATON_API_KEY не найден в .env файле.")
    sys.exit(1)

file_path = "/Users/higherpower/Downloads/VIDEO-2026-07-16-16-25-56.mp4"

def upload_video(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не существует.")
        return None

    print(f"Загрузка {file_path}...")
    size = os.path.getsize(file_path)
    
    # Определяем Content-Type
    content_type = "video/mp4"
    if file_path.lower().endswith(".mov"):
        content_type = "video/quicktime"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Upload-Content-Length": str(size),
        "X-Upload-Content-Type": content_type
    }
    
    metadata = {
        "snippet": {
            "title": os.path.basename(file_path),
            "description": "Загружено через Maton.ai",
            "tags": ["maton", "ai", "youtube_upload"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False
        }
    }
    
    init_url = "https://gateway.maton.ai/youtube/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    
    try:
        r = requests.post(init_url, headers=headers, json=metadata, timeout=30)
        if r.status_code != 200:
            print(f"Ошибка инициализации загрузки: {r.status_code} {r.text}")
            return None
            
        upload_url = r.headers.get("Location")
        if not upload_url:
            print("Ошибка: заголовок Location не найден в ответе.")
            return None
            
        print("Получен URL для загрузки. Отправка видеоданных...")
        put_headers = {
            "Content-Type": content_type
        }
        
        with open(file_path, "rb") as f:
            r2 = requests.put(upload_url, headers=put_headers, data=f)
            
        if r2.status_code in [200, 201]:
            video_id = r2.json().get("id")
            video_url = f"https://youtu.be/{video_id}"
            print(f"УСПЕШНО: {file_path} -> {video_url}")
            return video_url
        else:
            print(f"Ошибка при отправке данных: {r2.status_code} {r2.text}")
            return None
    except Exception as e:
        print(f"Исключение при загрузке: {e}")
        return None

if __name__ == "__main__":
    link = upload_video(file_path)
    if link:
        print(f"\nЗагрузка завершена! Ссылка: {link}")
    else:
        print("\nНе удалось загрузить видео.")
