import os
import json
import time
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Загрузка окружения
load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Настройка путей
BASE_DIR = Path(__file__).parent.parent
LOG_FILE = BASE_DIR / "logs" / "production_log.md"
PROMPTS_FILE = BASE_DIR / "docs" / "generation_prompts.json"
OUTPUT_DIR = BASE_DIR / "outputs" / "clips_v3"
PHOTO_PATH = BASE_DIR / "veo_director" / "photo_11_v4_1772301942427sit costume_coffee.png"

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def run_production():
    # Инициализация
    log_event("🚀 Запущена очередь производства видео клипов.")
    if not PHOTO_PATH.exists():
        log_event(f"❌ Ошибка: Фото не найдено по пути {PHOTO_PATH}")
        return

    client = genai.Client(api_key=API_KEY)
    
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    image_bytes = PHOTO_PATH.read_bytes()
    
    for i, scene in enumerate(data["scenes"]):
        scene_id = scene["id"]
        prompt_text = scene["prompt"]
        duration = scene.get("duration", 5)
        output_path = OUTPUT_DIR / f"{scene_id}.mp4"
        
        # Пропуск если файл уже есть
        if output_path.exists():
            log_event(f"⏩ Пропуск: сцена {scene_id} уже сгенерирована.")
            continue

        # Пауза между сценами для обхода RPM лимитов
        if i > 0:
            log_event("☕ Ожидание 180 секунд перед следующей сценой для соблюдения квот...")
            time.sleep(180)

        log_event(f"🎬 --- Сцена: {scene_id} ---")
        log_event(f"📝 Текст: {scene['text']}")
        log_event(f"🎥 Запуск генерации (Veo 3.1, {duration} сек)...")
        
        try:
            operation = client.models.generate_videos(
                model="models/veo-3.1-lite-generate-preview",
                source=types.GenerateVideosSource(
                    prompt=prompt_text,
                    image=types.Image(
                        image_bytes=image_bytes,
                        mime_type="image/png"
                    )
                ),
                config=types.GenerateVideosConfig(
                    number_of_videos=1,
                    aspect_ratio="9:16",
                    duration_seconds=duration
                )
            )
            
            op_name = operation.name
            log_event(f"⏳ Операция создана: {op_name}")
            
            # Опрос статуса
            start_time = time.time()
            while not operation.done:
                time.sleep(20)
                operation = client.operations.get(operation)
                elapsed = int(time.time() - start_time)
                log_event(f"   ... статус: {operation.done if operation.done else 'В процессе'} ({elapsed} сек)")
            
            # Обработка результата
            if hasattr(operation.response, "generated_videos"):
                vid = operation.response.generated_videos[0].video
                output_path = OUTPUT_DIR / f"{scene_id}.mp4"
                
                log_event(f"✅ Успех! Скачивание видео {vid.uri}...")
                
                # Скачивание через SDK
                # В google-genai 1.47.0 используется client.files.download
                # Но generated sample может быть уже в байтах или ссылкой
                video_data = client.files.download(file=vid)
                output_path.write_bytes(video_data)
                
                log_event(f"💾 СОХРАНЕНО: {output_path.name}")
            else:
                # RAI Filter или другая ошибка в ответе
                log_event(f"⚠️ Сцена отфильтрована или пустой ответ.")
                if hasattr(operation.response, "generate_video_response"):
                   resp = operation.response.generate_video_response
                   if resp.rai_media_filtered_count > 0:
                       log_event(f"🛑 RAI Filter: {resp.rai_media_filtered_reasons}")

        except Exception as e:
            log_event(f"🔥 КРИТИЧЕСКАЯ ОШИБКА в сцене {scene_id}: {str(e)}")

    log_event("🏁 Все сцены обработаны.")

if __name__ == "__main__":
    # Очистка лога перед началом
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    run_production()
