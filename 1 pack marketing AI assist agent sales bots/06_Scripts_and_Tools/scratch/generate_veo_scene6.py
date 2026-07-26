import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
model_name = "veo-3.1-generate-001"
prompt_text = 'Gritty 90s anime style, dark thriller anime. A laptop screen suddenly turns bright red. The two characters look at it in pure terror. English text on screen: "HACKED". The characters are shaking in fear.'
start_image_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip6_start_hacked.png"
output_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip6_video_silent.mp4"

try:
    with open(start_image_path, "rb") as f:
        start_bytes = f.read()
    start_img = types.Image(image_bytes=start_bytes, mime_type="image/png")
    
    print("Запуск генерации беззвучного видео (Сцена 6)...")
    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt_text,
        config=types.GenerateVideosConfig(
            reference_images=[types.VideoGenerationReferenceImage(image=start_img, reference_type="ASSET")],
            person_generation="ALLOW_ADULT",
            aspect_ratio="9:16",
            duration_seconds=8,
            generate_audio=False  # Отключаем кривой звук от Veo!
        )
    )
    
    while not operation.done:
        time.sleep(15)
        print(".", end="", flush=True)
        operation = client.operations.get(operation)
    print()
    
    if operation.error:
        print(f"Ошибка: {operation.error}")
    elif operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            with open(output_path, "wb") as f:
                f.write(video_obj.video_bytes)
            print(f"Видео сохранено: {output_path}")
        else:
            import google.cloud.storage as storage
            storage_client = storage.Client()
            gcs_uri = video_obj.uri
            path_parts = gcs_uri[5:].split("/", 1)
            bucket = storage_client.bucket(path_parts[0])
            blob = bucket.blob(path_parts[1])
            blob.download_to_filename(output_path)
            print(f"Видео сохранено (через GCS): {output_path}")
except Exception as e:
    print(f"Ошибка: {e}")
