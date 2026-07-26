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

def draw_text_with_outline(draw, text, x, y, font, text_color, outline_color, thickness):
    for dx in range(-thickness, thickness+1):
        for dy in range(-thickness, thickness+1):
            if dx*dx + dy*dy <= thickness*thickness:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def process_sticker(img_bytes, path, text, subtext):
    img = Image.open(BytesIO(img_bytes)).resize((512, 512), Image.Resampling.LANCZOS).convert('RGBA')
    
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if g > 180 and r < 100 and b < 100:
                pixels[x, y] = (0, 0, 0, 0)
    
    draw = ImageDraw.Draw(img)
    try:
        font_main = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    lines = text.split("\n")
    total_h = sum(draw.textbbox((0, 0), line, font=font_main)[3] - draw.textbbox((0, 0), line, font=font_main)[1] for line in lines) + 5 * (len(lines)-1)
    
    y_offset = 512 - total_h - 70
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (512 - w) / 2
        
        draw_text_with_outline(draw, line, x, y_offset, font_main, (0,0,0,255), (255,255,255,255), 10)
        y_offset += h + 5
    
    bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (512 - w_sub) / 2
    y_sub = 512 - 40
    
    draw_text_with_outline(draw, subtext, x_sub, y_sub, font_sub, (100,100,100,255), (255,255,255,255), 6)
    
    img.save(path, "PNG")
    print(f"Saved {path}")
    return path

def send(path):
    print(f"Sending {path} to TG...")
    with open(path, 'rb') as f:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID, 'caption': 'Вот тебе готовый прозрачный PNG стикер! Перешли его боту @Stickers для добавления в свой старый пак.'}, files={'document': f})

if __name__ == "__main__":
    t = get_access_token()
    prompts = [
        ("dozhim_skeleton.png", "A 2D vector die-cut sticker with a thick solid white border. A cinematic hyper-realistic portrait of a skeleton wearing a stylish modern business suit, sitting patiently at a sleek dark office desk holding a glowing smartphone. Cobwebs and dust around. Solid bright chroma key green background #00FF00, meme style, flat colors.", "ВСЁ ЕЩЕ ЖДУ\nНАШ СОЗВОН... 💀", "@nnsvt"),
        ("dozhim_search.png", "A 2D vector die-cut sticker with a thick solid white border. A cinematic hyper-realistic portrait of a stressed modern businesswoman acting like a detective in a dark office, shining a bright flashlight into the camera looking for a missing person. Solid bright chroma key green background #00FF00, meme style, flat colors.", "ВЫСЫЛАЮ\nПОИСКОВЫЙ ОТРЯД 🔦", "@nnsvt")
    ]
    
    for filename, prompt, text, subtext in prompts:
        b = generate(prompt, t)
        if b:
            process_sticker(b, filename, text, subtext)
            send(filename)
        print("Sleeping 65s for quota...")
        time.sleep(65)
