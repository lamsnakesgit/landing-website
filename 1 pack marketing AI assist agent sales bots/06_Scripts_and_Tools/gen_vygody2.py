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
    
    # Simple color replacement for bright green background
    # We look for pixels that are very green and make them transparent
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if g > 180 and r < 100 and b < 100:
                pixels[x, y] = (0, 0, 0, 0)
    
    draw = ImageDraw.Draw(img)
    try:
        font_main = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 54)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    # Draw main text
    bbox = draw.textbbox((0, 0), text, font=font_main)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (512 - w) / 2
    y = 512 - h - 60
    
    draw_text_with_outline(draw, text, x, y, font_main, (0,0,0,255), (255,255,255,255), 10)
    
    # Draw subtext
    bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (512 - w_sub) / 2
    y_sub = 512 - 40
    
    draw_text_with_outline(draw, subtext, x_sub, y_sub, font_sub, (100,100,100,255), (255,255,255,255), 6)
    
    img.save(path, "PNG")
    print(f"Saved {path}")
    return path

def upload_sticker(path):
    # Upload to telegram server to get file_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
    with open(path, 'rb') as f:
        resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files={'sticker': f})
    res = resp.json()
    if res.get('ok'):
        return res['result']['file_id']
    else:
        print("Upload failed:", res)
        return None

def create_sticker_set(name, title, file_ids):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createNewStickerSet"
    stickers = [{"sticker": fid, "emoji_list": ["🔥", "💰"]} for fid in file_ids]
    payload = {
        'user_id': CHAT_ID,
        'name': name,
        'title': title,
        'stickers': stickers,
        'sticker_format': 'static'
    }
    resp = requests.post(url, json=payload)
    print("Create set response:", resp.json())
    return resp.json().get('ok')

if __name__ == "__main__":
    t = get_access_token()
    prompts = [
        ("sticker_tongue.png", "A 2D vector die-cut sticker with a thick solid white border. A literal giant tongue wearing cool pixelated thug-life sunglasses, holding a glowing sack of money. Solid bright chroma key green background #00FF00, meme style, flat colors.", "ЯЗЫК ВЫГОД", "@nnsvt")
    ]
    
    file_ids = []
    for filename, prompt, text, subtext in prompts:
        b = generate(prompt, t)
        if b:
            process_sticker(b, filename, text, subtext)
            fid = upload_sticker(filename)
            if fid:
                file_ids.append(fid)
        
    if file_ids:
        # Get bot username
        me_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe").json()
        bot_username = me_resp['result']['username']
        
        pack_name = f"vygody_{int(time.time())}_by_{bot_username}"
        success = create_sticker_set(pack_name, "NNSVT Sales Pack", file_ids)
        if success:
            pack_url = f"https://t.me/addstickers/{pack_name}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"Твой стикерпак готов!\nДобавляй: {pack_url}"})
