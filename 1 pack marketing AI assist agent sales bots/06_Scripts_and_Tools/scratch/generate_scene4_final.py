import os
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

out_video_silent = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip4_correct_silent.mp4"
start_img = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_correct_start.png"

with open(start_img, "rb") as f:
    img_bytes = f.read()
img = types.Image(image_bytes=img_bytes, mime_type="image/png")

print("Запуск генерации видео...")
op = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="A young developer intensely typing and pressing the ENTER key on a mechanical keyboard. Cool blue and green screen glow reflecting on his face. Cinematic camera movement.",
    config=types.GenerateVideosConfig(
        reference_images=[types.VideoGenerationReferenceImage(image=img, reference_type="ASSET")],
        person_generation="ALLOW_ADULT", aspect_ratio="9:16", duration_seconds=8, generate_audio=False
    )
)

while not op.done:
    time.sleep(15)
    print(".", end="", flush=True)
    op = client.operations.get(op)
print("\nВидео сгенерировано.")

video_obj = op.result.generated_videos[0].video
if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
    with open(out_video_silent, "wb") as f:
        f.write(video_obj.video_bytes)
else:
    import google.cloud.storage as storage
    storage_client = storage.Client()
    path_parts = video_obj.uri[5:].split("/", 1)
    bucket = storage_client.bucket(path_parts[0])
    bucket.blob(path_parts[1]).download_to_filename(out_video_silent)

# Генерация аудио
os.system('''say -v "Yuri" -r 200 "А ИИ сможет прессовать, как Баке?" -o "aha_c.aiff"''')
os.system('''say -v "Yuri" -r 170 "Он будет делать это в тысячу раз хуже... Запускаем поток!" -o "mansik_c.aiff"''')
os.system('''ffmpeg -y -i aha_c.aiff -i mansik_c.aiff -filter_complex "[0:0][1:0]concat=n=2:v=0:a=1[out]" -map "[out]" "combined_c.aiff"''')
os.system(f'''ffmpeg -y -i "{out_video_silent}" -i "combined_c.aiff" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_correct_final.mp4"''')
print("Успешно завершено!")
