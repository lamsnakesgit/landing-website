import os
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
model_name = "veo-3.1-generate-001"

def gen_video(img_path, prompt, out_path):
    print(f"Запуск генерации: {out_path}")
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    img = types.Image(image_bytes=img_bytes, mime_type="image/png")
    
    op = client.models.generate_videos(
        model=model_name, prompt=prompt,
        config=types.GenerateVideosConfig(
            reference_images=[types.VideoGenerationReferenceImage(image=img, reference_type="ASSET")],
            person_generation="ALLOW_ADULT", aspect_ratio="9:16", duration_seconds=8, generate_audio=False
        )
    )
    
    while not op.done:
        time.sleep(15)
        print(".", end="", flush=True)
        op = client.operations.get(op)
    print("\nГотово!")
    
    if op.error:
        print(f"Ошибка: {op.error}")
        return
        
    video_obj = op.result.generated_videos[0].video
    if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
        with open(out_path, "wb") as f:
            f.write(video_obj.video_bytes)
    else:
        import google.cloud.storage as storage
        storage_client = storage.Client()
        gcs_uri = video_obj.uri
        path_parts = gcs_uri[5:].split("/", 1)
        bucket = storage_client.bucket(path_parts[0])
        blob = bucket.blob(path_parts[1])
        blob.download_to_filename(out_path)

gen_video(
    "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip7_start_panic.png",
    'Gritty 90s anime style, cyberpunk anime. A panicked young developer typing frantically on a mechanical keyboard. Red binary code and error messages reflect vividly in his round glasses. Fast-paced hacking scene.',
    "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip7_silent.mp4"
)

gen_video(
    "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip8_start_sparks.png",
    'Gritty 90s anime style, dramatic anime style. A laptop screen violently short-circuits with sparks flying, then the screen dies completely. The entire garage plunges into total darkness. Fast camera pull back.',
    "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip8_silent.mp4"
)

os.system('''say -v "Yuri" -r 180 "Я пытаюсь отрубить серваки, но он переписал доступы через n8n! Он сам себя защищает!" -o "04_renders/scene7_audio.aiff"''')
os.system('''ffmpeg -y -i "04_renders/clip7_silent.mp4" -i "04_renders/scene7_audio.aiff" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip7_final.mp4"''')

os.system('''say -v "Yuri" -r 140 "Бляяя... Всё. Серваки легли. Мы... мы в жопе, Баке." -o "04_renders/scene8_audio.aiff"''')
os.system('''ffmpeg -y -i "04_renders/clip8_silent.mp4" -i "04_renders/scene8_audio.aiff" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip8_final.mp4"''')
