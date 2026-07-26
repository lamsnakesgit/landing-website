import os
import sys
import time
from google import genai
from google.genai import types
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

def log(msg):
    print(msg, flush=True)

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
    storage_client = storage.Client()
except Exception as e:
    log(f"Ошибка инициализации клиента: {e}")
    sys.exit(1)

model_name = "veo-3.1-generate-001"
prompt_text = 'Gritty 90s anime style, dark thriller anime. Close-up of two young guys in a dark garage. One is panicking, shaking the other\'s shoulder. The second guy gets a determined look. Russian speech: "У нас нет... Но у Баке куча других должников. Мы соберем для него ИИ-агента!"'
start_image_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip2_start_dark_anime_1779739497101.png"
output_filename = "clip2_v2_final_8s.mp4"
duration_seconds = 8
generate_audio = True

log(f"Запускаем генерацию Сцены 2 через модель {model_name}...")

try:
    with open(start_image_path, "rb") as f:
        start_bytes = f.read()
    start_img = types.Image(image_bytes=start_bytes, mime_type="image/png")

    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt_text,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            duration_seconds=duration_seconds,
            person_generation="ALLOW_ADULT",
            generate_audio=generate_audio,
            reference_images=[types.VideoGenerationReferenceImage(image=start_img, reference_type="ASSET")]
        )
    )
    log(f"Операция успешно создана: {operation.name}")
    
    while not operation.done:
        time.sleep(15)
        log("Проверяем...")
        operation = client.operations.get(operation)
        
    log("Генерация завершена!")
    if operation.error:
        log(f"Ошибка операции: {operation.error}")
        sys.exit(1)
        
    if operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        out_path = os.path.join("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders", output_filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            with open(out_path, "wb") as f:
                f.write(video_obj.video_bytes)
            log(f"Видео успешно сохранено: {out_path}")
            sys.exit(0)
            
        gcs_uri = video_obj.uri
        if gcs_uri and gcs_uri.startswith("gs://"):
            path_parts = gcs_uri[5:].split("/", 1)
            bucket_name = path_parts[0]
            blob_name = path_parts[1]
            
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.download_to_filename(out_path)
            log(f"Видео успешно сохранено: {out_path}")
            sys.exit(0)
        else:
            log(f"Неизвестный формат URI: {gcs_uri}")
            sys.exit(1)
    else:
        log("В ответе нет видео.")
        sys.exit(1)

except Exception as e:
    log(f"Произошла ошибка при генерации: {e}")
    sys.exit(1)
