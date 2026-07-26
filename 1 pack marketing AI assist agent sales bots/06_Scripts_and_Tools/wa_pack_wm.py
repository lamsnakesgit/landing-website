import os, requests, zipfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"
REG_PACK = "nns_r_1781337023_by_test14fbot"

def draw_watermark(img, text="@nnsvt | AI Agents"):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    padding = 16
    x_center = 256
    y_center = 512 - th - 20
    
    x0 = x_center - tw/2 - padding
    y0 = y_center - padding/2
    x1 = x_center + tw/2 + padding
    y1 = y_center + th + padding/2
    
    draw.rounded_rectangle([x0, y0, x1, y1], radius=15, fill=(0, 0, 0, 160))
    draw.text((x_center - tw/2, y_center), text, font=font, fill=(255, 255, 255, 255))
    return img

def create_wa_pack():
    os.makedirs("wa_pack_wm", exist_ok=True)
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': 'Начинаю сборку WhatsApp-пака. Рисую водяной знак "@nnsvt | AI Agents" на всех 27 картинках...'})
    
    pack_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getStickerSet?name={REG_PACK}").json()
    if not pack_resp.get('ok'):
        return
        
    stickers = pack_resp['result']['stickers']
    
    for i, st in enumerate(stickers):
        file_id = st['file_id']
        f_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
        if f_resp.get('ok'):
            file_path = f_resp['result']['file_path']
            img_data = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}").content
            img = Image.open(BytesIO(img_data)).convert("RGBA")
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            img = draw_watermark(img)
            img.save(f"wa_pack_wm/wa_sticker_{i}.webp", "WEBP")
            
    zip_name = "whatsapp_watermarked.zip"
    with zipfile.ZipFile(zip_name, "w") as zf:
        for root, dirs, files in os.walk("wa_pack_wm"):
            for file in files:
                if file.endswith(".webp"):
                    zf.write(os.path.join(root, file), file)

    with open(zip_name, "rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
            data={'chat_id': CHAT_ID, 'caption': '📦 Твои стикеры для WhatsApp (с водяным знаком @nnsvt | AI Agents на каждой картинке!).\n\nЗакинь их через Sticker Maker.'}, 
            files={'document': f}
        )

if __name__ == "__main__":
    create_wa_pack()
