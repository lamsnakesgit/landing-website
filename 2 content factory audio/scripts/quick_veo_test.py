import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("GOOGLE_API_KEY")
PHOTO_PATH = BASE_DIR / "veo_director" / "photo_11_v4_1772301942427sit costume_coffee.png"
OUTPUT_PATH = BASE_DIR / "outputs" / "veo_avatar_test.mp4"

def generate_quick_test():
    if not API_KEY:
        print("ERROR: GOOGLE_API_KEY not found in .env")
        return

    print("🚀 Инициализация клиента GenAI...")
    client = genai.Client(api_key=API_KEY)

    print(f"📸 Чтение и кодирование фото: {PHOTO_PATH.name}")
    try:
        import base64
        image_bytes = PHOTO_PATH.read_bytes()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        print(f"✅ Фото закодировано.")
    except Exception as e:
        print(f"❌ Ошибка кодирования фото: {e}")
        return

    # Промпт по «Золотой формуле» Скилла
    # [Камера] + [Объект] + [Действие/Речь] + [Окружение] + [Свет] + [Качество]
    prompt_text = (
        "Cinematic professional close-up of the woman from the reference photo. "
        "The person is naturally talking directly to the camera in Russian with synchronized lip movements. "
        "Modern minimalist office background with soft bokeh, professional corporate lighting. "
        "Shot on 35mm lens, realistic skin texture, 4k high-resolution."
    )

    print(f"🎥 Запуск генерации видео (модель models/veo-3.1-generate-preview)...")
    print(f"Промпт: {prompt_text}")

    try:
        operation = client.models.generate_videos(
            model="models/veo-3.1-generate-preview",
            source=types.GenerateVideosSource(
                prompt=prompt_text,
                image=types.Image(
                    image_bytes=image_bytes,
                    mime_type="image/png"
                )
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                aspect_ratio="9:16"
            )
        )

        print(f"⏳ Операция запущена: {operation.name}")
        print("Ожидание завершения (обычно 3-5 минут)...")

        # Опрос статуса
        start_time = time.time()
        print(f"Опрос операции {operation.name}...")
        while not operation.done:
            time.sleep(20)
            try:
                # В некоторых версиях SDK .get() требует объект, в других — строку.
                # Попробуем обновить объект операции.
                operation = client.operations.get(operation)
            except Exception as poll_error:
                print(f"Ошибка при опросе (пробуем продолжить): {poll_error}")
            
            elapsed = int(time.time() - start_time)
            print(f"... Прошло {elapsed} сек. (Завершено: {operation.done})")

        if operation.error:
            print(f"❌ Ошибка генерации: {operation.error}")
            return

        print("✅ Генерация завершена! Скачивание видео...")
        
        result = operation.result()
        if not result or not result.generated_videos:
            print("❌ Видео не найдено в ответе.")
            return

        video = result.generated_videos[0]
        
        # Сохранение
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        # В новом SDK скачивание может быть через client.files или напрямую если есть байты
        # Обычно это URI, который нужно скачать. 
        # Но если есть video_bytes, используем их.
        
        # Используем встроенный метод сохранения если он есть в объекте
        # В 1.47.0 обычно video.video_bytes или требует скачивания через client.files
        
        # Попробуем скачать через files.download если это File объект
        try:
            # video.video - это объект File
            file_data = client.files.download(file=video.video)
            OUTPUT_PATH.write_bytes(file_data)
            print(f"🎉 УСПЕХ! Видео сохранено в: {OUTPUT_PATH}")
        except Exception as download_error:
            print(f"⚠️ Ошибка при скачивании через API: {download_error}")
            print("Пробую альтернативный метод...")
            # Fallback: если видео уже пришло в байтах (бывает для маленьких превью)
            if hasattr(video.video, 'video_bytes') and video.video.video_bytes:
                OUTPUT_PATH.write_bytes(video.video.video_bytes)
                print(f"🎉 УСПЕХ! Видео сохранено (из байтов) в: {OUTPUT_PATH}")
            else:
                print("Не удалось получить данные видео.")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    generate_quick_test()
