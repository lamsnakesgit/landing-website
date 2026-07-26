import os
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

img_out = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_anime_start.png"
video_out = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip4_anime_silent.mp4"

print("Генерация 2D аниме картинки...")
try:
    res = client.models.generate_images(
        model='imagen-3.0-generate-001',
        prompt='Gritty 90s anime style, 2D hand-drawn animation, dark thriller anime. Two young guys in a dark garage. One guy sitting at a computer, intensely pressing the ENTER key on a mechanical keyboard. The other guy stands behind him. Cool blue and green screen glow reflecting on their faces. Cinematic shadows, cel-shaded anime aesthetic.',
        config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/png", aspect_ratio="9:16")
    )
    with open(img_out, "wb") as f:
        f.write(res.generated_images[0].image.image_bytes)
except Exception as e:
    print(f"Ошибка картинки: {e}")

print("Запуск Veo Видео...")
with open(img_out, "rb") as f:
    img_bytes = f.read()
img = types.Image(image_bytes=img_bytes, mime_type="image/png")

op = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="2D anime style. A young developer intensely typing and pressing the ENTER key on a mechanical keyboard. Cool blue and green screen glow reflecting on his face. Cinematic camera movement.",
    config=types.GenerateVideosConfig(
        reference_images=[types.VideoGenerationReferenceImage(image=img, reference_type="ASSET")],
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

print("Склейка с аудио...")
os.system(f'''ffmpeg -y -i "{video_out}" -i "combined_c.aiff" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_anime_final.mp4"''')
print("Успешно!")
