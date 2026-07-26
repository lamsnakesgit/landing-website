import os
import time
import urllib.request
import uuid
import mimetypes
import subprocess
from pathlib import Path
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"
client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")

prompt = 'A photorealistic vertical close-up video of a confident 30-year-old male construction expert wearing a neat black polo shirt, standing in a bright modern apartment. He looks directly at the camera and says in Russian "Делаете ремонт в Бишкеке? Забудьте про скучные потолки. Мы ставим трендовые световые линии". High quality, realistic lip movements, cinematic lighting. No text overlays.'

def multipart_form(fields, files):
    boundary = "----ClineBoundary" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode())
        body.extend(b"\r\n")
    for name, path in files.items():
        path = Path(path)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode())
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary

print("Reading reference image...")
with open("studio_face.png", "rb") as f:
    img_bytes = f.read()

ref_image = types.VideoGenerationReferenceImage(
    image=types.Image(image_bytes=img_bytes, mime_type="image/png"),
    reference_type="ASSET"
)

print("Starting generation for Scene 1 with 9:16 and reference face...")
try:
    response = client.models.generate_videos(
        model='veo-3.1-generate-001',
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            person_generation="ALLOW_ADULT",
            reference_images=[ref_image]
        )
    )
    
    operation = response
    while not operation.done:
        print("Still generating...")
        time.sleep(15)
        operation = client.operations.get(operation)
        
    if operation.error:
        print("Error:", operation.error)
    else:
        print("Success! Saving video...")
        for i, video in enumerate(operation.result.generated_videos):
            VIDEO_PATH = "scene1_avatar_9_16.mp4"
            with open(VIDEO_PATH, "wb") as f:
                f.write(video.video.video_bytes)
            print(f"Saved {VIDEO_PATH}!")
            
            # Extract last frame using ffmpeg
            LAST_FRAME_PATH = "scene1_last_frame.jpg"
            print("Extracting last frame...")
            subprocess.run([
                "ffmpeg", "-y", "-sseof", "-0.1", "-i", VIDEO_PATH, 
                "-update", "1", "-q:v", "1", LAST_FRAME_PATH
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Send to Telegram
            BOT_TOKEN = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
            CHAT_ID = "888005446"

            # Send Video
            body, boundary = multipart_form(
                {"chat_id": CHAT_ID, "caption": "Сцена 1 (9:16, с реф-лицом) 🚀"},
                {"video": VIDEO_PATH},
            )
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST"
            )
            urllib.request.urlopen(req, timeout=90)
            
            # Send Last Frame
            if os.path.exists(LAST_FRAME_PATH):
                body2, boundary2 = multipart_form(
                    {"chat_id": CHAT_ID, "caption": "Последний кадр для бесшовной склейки следующей сцены"},
                    {"photo": LAST_FRAME_PATH},
                )
                req2 = urllib.request.Request(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data=body2, headers={"Content-Type": f"multipart/form-data; boundary={boundary2}"}, method="POST"
                )
                urllib.request.urlopen(req2, timeout=90)
                print("Last frame sent successfully.")

except Exception as e:
    import traceback
    traceback.print_exc()
