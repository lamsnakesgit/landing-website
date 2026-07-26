import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации: {e}")
    sys.exit(1)

model_name = "veo-3.1-generate-001"
prompt_text = 'Gritty 90s anime style, cyberpunk anime. Macro close-up of a glowing computer screen showing a node-based visual programming interface. A green button with the text "EXECUTE" is glowing and pulsating, a cursor clicks it. Russian speech: "Еще жестче. Бот готов. Запускаем поток!"'

# Используем только стартовый кадр
start_image_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_start_execute.png"
output_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip4_v1_final.mp4"

try:
    with open(start_image_path, "rb") as f:
        start_bytes = f.read()
    start_img = types.Image(image_bytes=start_bytes, mime_type="image/png")
    
    print(f"Запуск генерации видео (Сцена 4) через {model_name}...")
    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt_text,
        config=types.GenerateVideosConfig(
            reference_images=[types.VideoGenerationReferenceImage(image=start_img, reference_type="ASSET")],
            person_generation="ALLOW_ADULT",
            aspect_ratio="9:16",
            duration_seconds=8
        )
    )
    
    print("Ожидание завершения (это займет несколько минут)...")
    while not operation.done:
        time.sleep(15)
        print(".", end="", flush=True)
        operation = client.operations.get(operation)
    print()
    
    if operation.error:
        print(f"Ошибка генерации: {operation.error}")
    elif operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        
        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            with open(output_path, "wb") as f:
                f.write(video_obj.video_bytes)
            print(f"Видео успешно сохранено: {output_path}")
        else:
            # Пытаемся скачать по GCS URI
            import google.cloud.storage as storage
            storage_client = storage.Client()
            gcs_uri = video_obj.uri
            if gcs_uri and gcs_uri.startswith("gs://"):
                path_parts = gcs_uri[5:].split("/", 1)
                bucket = storage_client.bucket(path_parts[0])
                blob = bucket.blob(path_parts[1])
                blob.download_to_filename(output_path)
                print(f"Видео успешно сохранено (скачано с GCS): {output_path}")
    else:
        print("Видео не было сгенерировано.")
        
except Exception as e:
    print(f"Произошла ошибка: {e}")
