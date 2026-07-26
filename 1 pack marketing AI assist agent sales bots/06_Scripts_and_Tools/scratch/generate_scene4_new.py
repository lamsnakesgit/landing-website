import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

# 1. Генерируем End Frame (картинка конца)
end_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_new_end.png"
print("Генерация End Frame...")
try:
    res = client.models.generate_images(
        model='imagen-3.0-generate-001',
        prompt='Gritty 90s anime style, dark thriller anime, extreme low angle. The massive bald man in a leather jacket slams his fist down violently on the table. Motion blur, intense anger, yelling. Dramatic red and neon lighting, highly detailed.',
        config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/png", aspect_ratio="9:16")
    )
    with open(end_path, "wb") as f:
        f.write(res.generated_images[0].image.image_bytes)
except Exception as e:
    print(f"Ошибка картинки: {e}")

# 2. Генерируем Видео Veo (без звука)
start_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip_new_harsh.png"
video_out = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip4_harsh_silent.mp4"

print("Запуск Veo Видео...")
with open(start_path, "rb") as f:
    s_bytes = f.read()
img_start = types.Image(image_bytes=s_bytes, mime_type="image/png")

# Если End Frame сгенерировался, используем его тоже, но для надежности лучше только Start Frame + prompt
op = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="A massive bald man in a leather jacket leaning over the table. He firmly places his hand on the table. Serious expression, cinematic lighting, dramatic camera movement.",
    config=types.GenerateVideosConfig(
        reference_images=[types.VideoGenerationReferenceImage(image=img_start, reference_type="ASSET")],
        person_generation="ALLOW_ADULT", aspect_ratio="9:16", duration_seconds=8, generate_audio=False
    )
)

while not op.done:
    time.sleep(15)
    print(".", end="", flush=True)
    op = client.operations.get(op)
print("\nVeo Готово!")

video_obj = op.result.generated_videos[0].video
if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
    with open(video_out, "wb") as f:
        f.write(video_obj.video_bytes)
else:
    import google.cloud.storage as storage
    storage_client = storage.Client()
    path_parts = video_obj.uri[5:].split("/", 1)
    bucket = storage_client.bucket(path_parts[0])
    bucket.blob(path_parts[1]).download_to_filename(video_out)

# 3. Аудио и Склейка
print("Генерация аудио и FFmpeg склейка...")
os.system('''say -v "Yuri" -r 200 "А ИИ сможет прессовать, как Баке?" -o "aha.aiff"''')
os.system('''say -v "Yuri" -r 170 "Он будет делать это в тысячу раз хуже. За секунду найдет всех их родственников и заблокирует счета." -o "mansik.aiff"''')
os.system('''ffmpeg -y -i aha.aiff -i mansik.aiff -filter_complex "[0:0][1:0]concat=n=2:v=0:a=1[out]" -map "[out]" "combined_audio.aiff"''')
os.system(f'''ffmpeg -y -i "{video_out}" -i "combined_audio.aiff" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_new_harsh_final.mp4"''')
print("Успешно завершено!")
