import os, requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

REG_PACK = "nns_r_1781337023_by_test14fbot"
EMOJI_PACK = "nns_e_1781337023_by_test14fbot"

files_to_fix = [
    ("sticker_tongue.png", ["👅", "💰"]),
    ("dozhim_skeleton.png", ["💀", "⏳"]),
    ("dozhim_search.png", ["🔦", "👀"])
]

def draw_text_with_outline(draw, text, x, y, font, text_color, outline_color, thickness):
    for dx in range(-thickness, thickness+1):
        for dy in range(-thickness, thickness+1):
            if dx*dx + dy*dy <= thickness*thickness:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def fix_image(file_path):
    img = Image.open(file_path).convert('RGBA')
    pixels = img.load()
    for y in range(460, 512):
        for x in range(512):
            pixels[x, y] = (0, 0, 0, 0)
    
    draw = ImageDraw.Draw(img)
    try:
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    except:
        font_sub = ImageFont.load_default()
        
    subtext = "@nnsvt"
    bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (512 - w_sub) / 2
    y_sub = 512 - 50
    
    draw_text_with_outline(draw, subtext, x_sub, y_sub, font_sub, (100,100,100,255), (255,255,255,255), 5)
    img.save(file_path, "PNG")
    
    emoji_path = file_path.replace(".png", "_emoji.png")
    img.resize((100, 100), Image.Resampling.LANCZOS).save(emoji_path, "PNG")
    return emoji_path

def upload_file(path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/uploadStickerFile"
    with open(path, "rb") as f:
        resp = requests.post(url, data={'user_id': CHAT_ID, 'sticker_format': 'static'}, files={'sticker': f})
    res = resp.json()
    if res.get('ok'):
        return res['result']['file_id']
    return None

def replace_stickers():
    reg_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={REG_PACK}").json()
    emo_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={EMOJI_PACK}").json()
    
    if not reg_resp.get('ok') or not emo_resp.get('ok'):
        print("Failed to fetch sets")
        return

    reg_stickers = reg_resp['result']['stickers']
    emo_stickers = emo_resp['result']['stickers']
    
    for i in range(3):
        file_path, emojis = files_to_fix[i]
        emoji_path = fix_image(file_path)
        
        fid_reg = upload_file(file_path)
        fid_emo = upload_file(emoji_path)
        
        # Replace in REG_PACK
        old_reg_fid = reg_stickers[-(3-i)]['file_id']
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/replaceStickerInSet", json={
            'user_id': CHAT_ID, 'name': REG_PACK, 'old_sticker': old_reg_fid, 
            'sticker': {'sticker': fid_reg, 'emoji_list': emojis}
        })
        
        # Replace in EMOJI_PACK
        old_emo_fid = emo_stickers[-(3-i)]['file_id']
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/replaceStickerInSet", json={
            'user_id': CHAT_ID, 'name': EMOJI_PACK, 'old_sticker': old_emo_fid, 
            'sticker': {'sticker': fid_emo, 'emoji_list': emojis}
        })

    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': '✅ Стер эту гигантскую простыню текста и аккуратно вернул крупный @nnsvt по центру! \n\nВ стикерпаке Телеграма изменения появятся сами через минуту (у Телеграма есть небольшой кеш).'})

if __name__ == "__main__":
    replace_stickers()
