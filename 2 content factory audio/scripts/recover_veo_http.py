import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("GOOGLE_API_KEY")
OP_ID = "models/veo-3.1-generate-preview/operations/8hab3ndmrrj9"
OUTPUT_PATH = BASE_DIR / "outputs" / "veo_avatar_test.mp4"

def recover_video_http():
    print(f"📡 Запрос к API напрямую (HTTP) для операции {OP_ID}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{OP_ID}?key={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("done"):
            print("⏳ Видео еще генерируется. Статус в облаке: не готово.")
            return

        if "error" in data:
            print(f"❌ Ошибка в облаке: {data['error']}")
            return

        print("✅ Готово! Извлекаем метаданные...")
        
        # В ответе Veo результат лежит в response -> generatedVideos
        vids = data.get("response", {}).get("generatedVideos", [])
        if not vids:
            print(f"❌ Видео не найдено в ответе. Полный ответ: {data}")
            return

        video_metadata = vids[0].get("video", {})
        file_name = video_metadata.get("name") # Это формат "files/..."
        
        if not file_name:
            print(f"❌ Не удалось найти имя файла для скачивания.")
            return

        print(f"📥 Скачивание файла {file_name}...")
        
        # Скачиваем сам файл через API
        download_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?alt=media&key={API_KEY}"
        file_response = requests.get(download_url)
        
        if file_response.status_code == 200:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_PATH.write_bytes(file_response.content)
            print(f"🎉 УСПЕХ! Видео весом {len(file_response.content)} байт сохранено в: {OUTPUT_PATH}")
        else:
            print(f"❌ Ошибка скачивания файла: {file_response.status_code} {file_response.text}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    recover_video_http()
