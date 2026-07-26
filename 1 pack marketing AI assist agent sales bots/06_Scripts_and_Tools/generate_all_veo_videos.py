import os
import sys
import time
import re
import requests
from google import genai
from google.genai import types

# Set correct credentials path for VPS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"

# Parse prompts from markdown
md_path = "smm_brand_ai/ai_content/love_stories/storyboard/veo31_vertex_generation_pack.md"
with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

global_prefix = "Vertical 9:16 realistic cinematic romantic short film in a cozy modern coffee shop in Almaty. Use the provided character reference images and preserve the same heroes, outfits, hair, body proportions, cafe location and warm cinematic style. The woman is the same young Kazakh woman in a beige knit sweater drawing in a sketchbook. The man is the same young Kazakh man in a black hoodie near the coffee bar. Smooth stabilized camera, natural emotional acting, warm cafe lighting, shallow depth of field, soft bokeh. No text overlays, no readable text, no subtitles, no logos, no watermark. "
global_negative = "different face, changed identity, changed outfit, changed hairstyle, distorted face, bad eyes, deformed hands, extra fingers, extra limbs, blurry face, face drift, inconsistent character, text, subtitles, logo, watermark, random letters, overexposed, oversaturated, low resolution, glitch, duplicate person, uncanny expression, shaky camera, extreme motion blur."

scenes = {}
# Regex to find scene number and its prompt
pattern = re.compile(r'## VEO-(\d{2}).*?```text\n(.*?)\n```', re.DOTALL)
matches = pattern.findall(md_content)
for match in matches:
    num, prompt = match
    scenes[num] = prompt.strip()

client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

frames_dir = "smm_brand_ai/ai_content/love_stories/storyboard/frames_raw"

for scene_num in sorted(scenes.keys()):
    if scene_num == "01": continue # already done
    
    start_img_path = f"{frames_dir}/veo31_{scene_num}_start.png"
    end_img_path = f"{frames_dir}/veo31_{scene_num}_end.png"
    
    if not os.path.exists(start_img_path):
        print(f"Propuskayu VEO-{scene_num}: net startovogo kadra")
        continue
        
    print(f"--- Generator VEO-{scene_num} ---")
    
    start_image = types.Image(image_bytes=open(start_img_path, "rb").read(), mime_type="image/png")
    end_image = types.Image(image_bytes=open(end_img_path, "rb").read(), mime_type="image/png") if os.path.exists(end_img_path) else None
    
    config = types.GenerateVideosConfig(
        person_generation="ALLOW_ADULT",
        aspect_ratio="9:16",
        duration_seconds=8,
        negative_prompt=global_negative
    )
    if end_image:
        config.last_frame = end_image
        
    full_prompt = global_prefix + scenes[scene_num]
    
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-001",
            prompt=full_prompt,
            image=start_image,
            config=config
        )
        
        while not operation.done:
            time.sleep(15)
            print(".", end="", flush=True)
            operation = client.operations.get(operation)
        print()
        
        if operation.error:
            print(f"Oshibka VEO-{scene_num}: {operation.error}")
        elif operation.result and operation.result.generated_videos:
            video_obj = operation.result.generated_videos[0].video
            output_file = f"veo31_{scene_num}_final.mp4"
            with open(output_file, "wb") as f:
                f.write(video_obj.video_bytes)
            
            # Send to TG
            with open(output_file, 'rb') as f:
                requests.post(API_URL, data={'chat_id': CHAT_ID, 'caption': f'VEO-{scene_num} gotov!'}, files={'video': f})
            os.remove(output_file)
            print(f"VEO-{scene_num} otpravlen v TG.")
    except Exception as e:
        print(f"Exception na VEO-{scene_num}: {e}")

