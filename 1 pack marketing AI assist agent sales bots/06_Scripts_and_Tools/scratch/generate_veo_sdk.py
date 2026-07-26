import os
import sys
import base64
import time
from google import genai
from google.genai import types

# Указываем сервисный аккаунт
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

def log(msg):
    print(msg, flush=True)

log("Инициализируем клиент Google GenAI...")
try:
    # Инициализируем клиент с принудительным указанием проекта
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
    log("Клиент успешно инициализирован.")
except Exception as e:
    log(f"Ошибка инициализации клиента: {e}")
    sys.exit(1)

# Читаем референсные кадры
try:
    with open("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_start.png", "rb") as f:
        img_start_data = f.read()
    with open("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_end.png", "rb") as f:
        img_end_data = f.read()
    log("Изображения успешно загружены.")
except Exception as e:
    log(f"Ошибка загрузки изображений: {e}")
    sys.exit(1)

# Вызываем veo-2.0-generate-001 или veo-3.0-generate-preview
# Мы знаем, что veo-2.0-generate-001 является стабильной моделью в Vertex
model_name = "veo-2.0-generate-001"
prompt = (
    "Cinematic realism, close-up, low angle. A polished black leather boot stepping out of a dark Land Cruiser door onto gravel. "
    "The video must start exactly like the start reference image and end exactly like the end reference image. Realistic camera motion."
)

log(f"Запускаем генерацию видео через модель {model_name}...")

try:
    # Подготавливаем config
    config = {
        "aspect_ratio": "9:16",
        "duration_seconds": 5,
        "person_generation": "ALLOW_ADULT",
        "generate_audio": True
    }
    
    # Запускаем генерацию
    # В новом SDK Vertex AI методы могут отличаться, проверим через generate_videos
    # Для image-to-video в Veo передаем входные изображения
    # В SDK обычно используется generate_videos
    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            duration_seconds=5,
            person_generation="ALLOW_ADULT",
            generate_audio=False
        )
    )
    log(f"Операция успешно создана. Имя операции: {operation.name}")
    
    # Поллинг
    log("Начинаем опрашивать статус (каждые 15 секунд)...")
    while not operation.done:
        time.sleep(15)
        log("Проверяем...")
        operation = client.operations.get(operation)
        
    log("Генерация завершена!")
    if operation.error:
        log(f"Ошибка операции: {operation.error}")
        sys.exit(1)
        
    # Сохраняем результат
    if operation.result and operation.result.generated_videos:
        video_bytes = operation.result.generated_videos[0].video.bytes
        out_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip1_dynamic_sound.mp4"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(video_bytes)
        log(f"Видео успешно сохранено в {out_path}")
        sys.exit(0)
    else:
        log("В ответе нет сгенерированного видео.")
        sys.exit(1)

except Exception as e:
    log(f"Произошла ошибка при генерации: {e}")
    sys.exit(1)
