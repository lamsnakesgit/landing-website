import os
import sys
import time
import requests
from google import genai
from google.genai import types

# Credentials for Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации Vertex AI: {e}")
    sys.exit(1)

model_name = "veo-3.1-generate-001"
output_file = "veo_01_love_story.mp4"
prompt = 'Vertical 9:16 realistic cinematic opening shot of a cozy modern coffee shop in Almaty on a rainy evening. Warm golden light glows from the windows, raindrops on the glass, soft reflections on the wet street, calm romantic atmosphere. Smooth slow dolly toward the coffee shop window, stabilized, shallow depth of field. A female voiceover says in Russian "Я приходила в эту кофейню просто рисовать.". No text overlays, no watermarks, no written text.'

# Load start and end frames
start_frame_path = "smm_brand_ai/ai_content/love_stories/storyboard/frames_selected/veo31_01_start.png"
end_frame_path = "smm_brand_ai/ai_content/love_stories/storyboard/frames_selected/veo31_01_end.png"

start_image = types.Image(image_bytes=open(start_frame_path, "rb").read(), mime_type="image/png") if os.path.exists(start_frame_path) else None
end_image = types.Image(image_bytes=open(end_frame_path, "rb").read(), mime_type="image/png") if os.path.exists(end_frame_path) else None

print("Запуск генерации VEO-01 (Love Story) через Veo с начальным и конечным кадрами...")
try:
    config = types.GenerateVideosConfig(
        person_generation="ALLOW_ADULT",
        aspect_ratio="9:16",
        duration_seconds=8
    )
    if end_image:
        config.last_frame = end_image
        
    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt,
        image=start_image,
        config=config
    )
    
    print("Ожидание завершения (это займет несколько минут)...")
    while not operation.done:
        time.sleep(10)
        print(".", end="", flush=True)
        operation = client.operations.get(operation)
    print()
    
    if operation.error:
        print(f"Ошибка генерации: {operation.error}")
    elif operation.result and operation.result.generated_videos:
        video_obj = operation.result.generated_videos[0].video
        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            with open(output_file, "wb") as f:
                f.write(video_obj.video_bytes)
            print(f"Видео успешно сгенерировано: {output_file}")
            
            # Send to Telegram
            print("Отправка в Telegram...")
            with open(output_file, 'rb') as f:
                response = requests.post(
                    API_URL, 
                    data={'chat_id': CHAT_ID, 'caption': 'VEO-01 (с картинками): Лав-стори кофейня (8 сек)'}, 
                    files={'video': f}
                )
            
            if response.status_code == 200:
                print("Видео успешно отправлено в Telegram!")
                # Remove to save space
                os.remove(output_file)
                print("Локальный файл удален.")
            else:
                print(f"Ошибка отправки в TG: {response.text}")
    else:
        print(f"Видео не было сгенерировано.")
except Exception as e:
    print(f"Ошибка: {e}")
