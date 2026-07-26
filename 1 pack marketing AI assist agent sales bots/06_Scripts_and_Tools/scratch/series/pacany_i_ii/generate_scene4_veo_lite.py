import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
    print("Клиент Vertex AI успешно инициализирован.")
except Exception as e:
    print(f"Ошибка инициализации Vertex AI: {e}")
    sys.exit(1)

renders_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders"
brain_dir = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6"

start_img_path = os.path.join(brain_dir, "clip4_anime_start.png")
output_filename = "clip4_veo31lite_native.mp4"
out_path = os.path.join(renders_dir, output_filename)

prompt = '2D anime style. A young developer intensely typing and pressing the ENTER key on a mechanical keyboard. Cool blue and green screen glow reflecting on his face. Cinematic camera movement. Russian speech: "Еще жестче. Бот готов. Запускаем поток!"'

print(f"Запуск генерации {output_filename} через veo-3.1-lite-generate-001 с аудио...")

try:
    with open(start_img_path, "rb") as f:
        start_bytes = f.read()
    start_img = types.Image(image_bytes=start_bytes, mime_type="image/png")

    operation = client.models.generate_videos(
        model="veo-3.1-lite-generate-001",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            reference_images=[types.VideoGenerationReferenceImage(image=start_img, reference_type="ASSET")],
            person_generation="ALLOW_ADULT",
            aspect_ratio="9:16",
            duration_seconds=8,
            generate_audio=True  # Включаем нативный звук
        )
    )
    
    print(f"Операция создана: {operation.name}. Ожидание...")
    while not operation.done:
        time.sleep(15)
        print(".", end="", flush=True)
        operation = client.operations.get(operation)
    print()
    
    if operation.error:
        print(f"Ошибка операции: {operation.error}")
        sys.exit(1)
        
    if operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            with open(out_path, "wb") as f:
                f.write(video_obj.video_bytes)
        else:
            import google.cloud.storage as storage
            storage_client = storage.Client()
            path_parts = video_obj.uri[5:].split("/", 1)
            bucket = storage_client.bucket(path_parts[0])
            bucket.blob(path_parts[1]).download_to_filename(out_path)
        
        print(f"Видео успешно сохранено в {out_path}")
        sys.exit(0)
    else:
        print("Нет видео в ответе.")
        sys.exit(1)

except Exception as e:
    print(f"Исключение при генерации: {e}")
    sys.exit(1)
