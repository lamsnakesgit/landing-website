import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("GOOGLE_API_KEY")
OP_ID = "models/veo-3.1-generate-preview/operations/8hab3ndmrrj9"
OUTPUT_PATH = BASE_DIR / "outputs" / "veo_avatar_test.mp4"

def recover_video():
    client = genai.Client(api_key=API_KEY)
    print(f"📡 Подключение к операции {OP_ID}...")
    
    try:
        # Обход бага SDK: создаем объект Operation вручную
        op_obj = types.Operation(name=OP_ID)
        op = client.operations.get(op_obj)
        
        if not op.done:
            print("⏳ Видео еще генерируется. Подожди минуту.")
            return

        print("✅ Готово! Извлекаем результат...")
        
        # В google-genai результат лежит в op.response
        if not hasattr(op, 'response') or not op.response.generated_videos:
            print(f"❌ Ответ пуст или ошибка: {op.error if hasattr(op, 'error') else 'Нет данных'}")
            return

        video_entry = op.response.generated_videos[0]
        
        # Скачивание. video_entry.video - это File объект
        print(f"📥 Скачивание файла {video_entry.video.name}...")
        
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Самый надежный способ скачивания в 1.47.0
        file_bytes = client.files.download(file=video_entry.video)
        OUTPUT_PATH.write_bytes(file_bytes)
        
        print(f"🎉 УСПЕХ! Видео весом {len(file_bytes)} байт сохранено в: {OUTPUT_PATH}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recover_video()
