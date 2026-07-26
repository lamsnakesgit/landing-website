import os
import requests
from PIL import Image, ImageDraw, ImageFont

slides = [
    {
        "headline": "CLAUDE ЗАБАНИЛИ.\nКТО ДАЛЬШЕ?",
        "subtext": "Сначала молча забанили Claude.\nДумаешь, это просто сбой?",
        "file": "slide_1_bg_1781554894145.png"
    },
    {
        "headline": "ШАГ ВЛЕВО — ПЕРМАБАН",
        "subtext": "Цензура ИИ дошла до абсурда.\nМодели отказываются писать код.",
        "file": "slide_2_bg_1781554907364.png"
    },
    {
        "headline": "ЭТОТ ИИ НЕ ТВОЙ",
        "subtext": "Ты платишь по $20 каждый месяц.\nНо тебя могут отключить в любую секунду.",
        "file": "slide_3_bg_1781554917698.png"
    },
    {
        "headline": "СВОЯ ЛИЧНАЯ\nНЕЙРОСЕТЬ",
        "subtext": "Выход только один. Поднять свою\nабсолютно независимую нейросеть.",
        "file": "slide_4_bg_1781554938991.png"
    },
    {
        "headline": "OPEN-SOURCE\nРВЕТ GPT-4",
        "subtext": "Открытые модели (Llama, DeepSeek) бесплатны.\nОни ставятся на твой личный сервер.",
        "file": "slide_5_bg_1781554950131.png"
    },
    {
        "headline": "ПИШИ СЛОВО:\nОТКРЫТЫЙ",
        "subtext": "Пиши мне в Директ кодовое слово,\nи я скину мануал по запуску ИИ.",
        "file": "slide_6_bg_1781554961661.png"
    }
]

base_dir = "/Users/higherpower/.gemini/antigravity/brain/c1edc89f-b82d-476c-8418-be8adaaf40a4"
out_dir = os.path.join(base_dir, "carousel_output_final")
os.makedirs(out_dir, exist_ok=True)

def add_watermark(img):
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    width, height = img.size
    try:
        font_watermark = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.025))
    except:
        font_watermark = ImageFont.load_default()
    
    text = "@lamanopro_"
    bbox = draw.textbbox((0, 0), text, font=font_watermark)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    x = width - text_width - int(height * 0.05) - int(height * 0.035)
    y = height - text_height - int(height * 0.05)
    
    draw.text((x, y), text, font=font_watermark, fill=(255, 255, 255, 200))
    
    # Draw blue verified badge
    circle_x = width - int(height * 0.05) - int(height * 0.015)
    circle_y = y + text_height // 2 - int(height * 0.015)
    radius = int(height * 0.015)
    draw.ellipse([circle_x, circle_y, circle_x + radius*2, circle_y + radius*2], fill="#1DA1F2")
    # checkmark
    check_points = [
        (circle_x + radius*0.5, circle_y + radius),
        (circle_x + radius*0.9, circle_y + radius*1.4),
        (circle_x + radius*1.5, circle_y + radius*0.6)
    ]
    draw.line(check_points, fill="white", width=max(2, int(radius*0.2)))
    
    return Image.alpha_composite(img, txt_layer)

def draw_text_on_image(img, headline, subtext):
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    width, height = img.size
    
    try:
        font_h1 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.06), index=1)
        font_p = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.035))
    except:
        font_h1 = ImageFont.load_default()
        font_p = ImageFont.load_default()
        
    box_h = int(height * 0.35)
    draw.rectangle([0, 0, width, box_h], fill=(0, 0, 0, 180))
    
    margin_x = int(width * 0.05)
    y_pos = int(height * 0.05)
    
    draw.text((margin_x, y_pos), headline, font=font_h1, fill="white", spacing=10)
    bbox = draw.multiline_textbbox((margin_x, y_pos), headline, font=font_h1, spacing=10)
    y_pos = bbox[3] + int(height * 0.02)
    
    draw.text((margin_x, y_pos), subtext, font=font_p, fill=(200, 200, 200), spacing=10)
    
    return Image.alpha_composite(img, txt_layer)

generated_files = []

for i, slide in enumerate(slides):
    idx = i + 1
    in_path = os.path.join(base_dir, slide["file"])
    out_path = os.path.join(out_dir, f"slide_{idx}_final.png")
    
    print(f"Обработка слайда {idx}...")
    try:
        img = Image.open(in_path).convert("RGBA")
        img = draw_text_on_image(img, slide["headline"], slide["subtext"])
        img = add_watermark(img)
        img.convert("RGB").save(out_path)
        generated_files.append(out_path)
        print(f"✅ Слайд {idx} готов: {out_path}")
    except Exception as e:
        print(f"Ошибка обработки слайда {idx}: {e}")

print("Отправка в Telegram...")
BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

for file_path in generated_files:
    try:
        with open(file_path, 'rb') as photo:
            requests.post(API_URL, data={'chat_id': CHAT_ID}, files={'photo': photo})
            print(f"Отправлено: {file_path}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

print("Готово!")
