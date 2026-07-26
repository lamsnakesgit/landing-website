import os, requests, time
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

files_to_upload = [
    ("sticker_tongue.png", ["👅", "💰"]),
    ("dozhim_skeleton.png", ["💀", "⏳"]),
    ("dozhim_search.png", ["🔦", "👀"])
]

def get_bot_username():
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe").json()
    return resp['result']['username']

def upload_file(path):
    print(f"Uploading {path}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
    with open(path, "rb") as f:
        resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files={'sticker': f})
    res = resp.json()
    if res.get('ok'):
        return res['result']['file_id']
    else:
        print(f"Upload failed for {path}:", res)
        return None

def create_pack(name, title, sticker_type, stickers):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createNewStickerSet"
    payload = {
        'user_id': CHAT_ID,
        'name': name,
        'title': title,
        'stickers': stickers,
        'sticker_format': 'static',
        'sticker_type': sticker_type
    }
    resp = requests.post(url, json=payload).json()
    print(f"Create pack {name}: {resp}")
    return resp.get('ok')

def draw_text_with_outline(draw, text, x, y, font, text_color, outline_color, thickness):
    for dx in range(-thickness, thickness+1):
        for dy in range(-thickness, thickness+1):
            if dx*dx + dy*dy <= thickness*thickness:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def update_image(file_path):
    img = Image.open(file_path).convert('RGBA')
    pixels = img.load()
    # clear bottom pixels (from y=460 to 512) to remove @nnsvt
    for y in range(460, 512):
        for x in range(512):
            pixels[x, y] = (0, 0, 0, 0)
    
    draw = ImageDraw.Draw(img)
    try:
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    except:
        font_sub = ImageFont.load_default()
        
    subtext = "@vacancydigitalaize | @unleash_assistant_bo"
    bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (512 - w_sub) / 2
    y_sub = 512 - 40
    
    draw_text_with_outline(draw, subtext, x_sub, y_sub, font_sub, (100,100,100,255), (255,255,255,255), 5)
    
    img.save(file_path, "PNG")
    
    emoji_path = file_path.replace(".png", "_emoji.png")
    img.resize((100, 100), Image.Resampling.LANCZOS).save(emoji_path, "PNG")
    return emoji_path

if __name__ == "__main__":
    bot_username = get_bot_username()
    ts = int(time.time())
    
    reg_stickers = []
    emoji_stickers = []
    
    for file_path, emojis in files_to_upload:
        if os.path.exists(file_path):
            emoji_path = update_image(file_path)
            
            fid_reg = upload_file(file_path)
            if fid_reg:
                reg_stickers.append({"sticker": fid_reg, "emoji_list": emojis})
                
            fid_emoji = upload_file(emoji_path)
            if fid_emoji:
                emoji_stickers.append({"sticker": fid_emoji, "emoji_list": emojis})

    if reg_stickers:
        reg_name = f"nnsvt_ai_{ts}_by_{bot_username}"
        if create_pack(reg_name, "AI Агенты | @vacancydigitalaize", "regular", reg_stickers):
            link = f"https://t.me/addstickers/{reg_name}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"✅ Основные стикеры готовы:\n{link}"})
            
    if emoji_stickers:
        emoji_name = f"nnsvt_emoji_{ts}_by_{bot_username}"
        if create_pack(emoji_name, "AI Эмодзи | @unleash_assistant_bo", "custom_emoji", emoji_stickers):
            link = f"https://t.me/addstickers/{emoji_name}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"⚡️ Кастомные эмодзи готовы:\n{link}"})
