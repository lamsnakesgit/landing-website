import os, time, base64, requests, google.auth
from google.auth.transport.requests import Request
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"

def get_access_token():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), "vertex_sa.json")
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(Request())
    return credentials.token

def generate(prompt, token):
    print(f"Generating: {prompt}")
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    payload = {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1, "aspectRatio": "1:1", "outputOptions": {"mimeType": "image/png"}}}
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return None
    data = resp.json()
    try:
        return base64.b64decode(data['predictions'][0]['bytesBase64Encoded'])
    except Exception as e:
        print(f"Failed to parse response: {e}")
        return None

def watermark(img_bytes, path, text):
    img = Image.open(BytesIO(img_bytes)).resize((512, 512), Image.Resampling.LANCZOS).convert('RGBA')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
    except:
        font = ImageFont.load_default()
    
    # Bottom center text
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (512 - w) / 2
    y = 512 - h - 30
    
    for dx in [-3,0,3]:
        for dy in [-3,0,3]:
            draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,255))
    draw.text((x, y), text, font=font, fill=(255,255,255,255))
    img.save(path, "PNG")
    print(f"Saved {path}")

def send(path):
    print(f"Sending {path} to TG...")
    with open(path, 'rb') as f:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID, 'caption': path}, files={'document': f})

if __name__ == "__main__":
    t = get_access_token()
    prompts = [
        ("vygody_megaphone.png", "A 2D vector die-cut sticker with a thick white border. A cool energetic businessman shouting into a megaphone, but instead of sound, glowing gold coins and diamonds are flying out of the megaphone. Solid white background, meme style, flat colors.", "ЯЗЫК ВЫГОД"),
        ("vygody_tongue.png", "A 2D vector die-cut sticker with a thick white border. A literal giant tongue wearing cool pixelated thug-life sunglasses, holding a glowing sack of money. Solid white background, meme style, flat colors.", "ЯЗЫК ВЫГОД")
    ]
    for filename, prompt, text in prompts:
        b = generate(prompt, t)
        if b:
            watermark(b, filename, text)
            send(filename)
        print("Sleeping 65s for quota...")
        time.sleep(65)
