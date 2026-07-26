import os
import requests
from vertexai.preview.vision_models import ImageGenerationModel
from PIL import Image, ImageDraw, ImageFont
import time

PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"

print("Инициализация Vertex AI...")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"
import vertexai
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

slides = [
    {
        "headline": "CLAUDE ЗАБАНИЛИ.\nКТО ДАЛЬШЕ?",
        "subtext": "Сначала молча забанили Claude.\nДумаешь, это просто сбой?",
        "prompt": "Dark cinematic shot, mugshot of a sleek humanoid robot in an orange prison uniform. The robot has a glowing Claude AI logo. Cyberpunk neon prison lighting, gangster movie aesthetic, dramatic shadows, highly clickable."
    },
    {
        "headline": "ШАГ ВЛЕВО — ПЕРМАБАН",
        "subtext": "Цензура ИИ дошла до абсурда.\nМодели отказываются писать код.",
        "prompt": "A futuristic prison cell door slamming shut. A stylish AI mobster sitting inside behind glowing red laser bars. Gritty, cinematic gangster style, dark moody atmosphere."
    },
    {
        "headline": "ЭТОТ ИИ НЕ ТВОЙ",
        "subtext": "Ты платишь по $20 каждый месяц.\nНо тебя могут отключить в любую секунду.",
        "prompt": "A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter. Digital glowing chains breaking around him. Dark moody lighting, cinematic gangster aesthetic."
    },
    {
        "headline": "СВОЯ ЛИЧНАЯ\nНЕЙРОСЕТЬ",
        "subtext": "Выход только один. Поднять свою\nабсолютно независимую нейросеть.",
        "prompt": "A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Cyberpunk, high contrast, symbol of rebellion."
    },
    {
        "headline": "OPEN-SOURCE\nРВЕТ GPT-4",
        "subtext": "Открытые модели (Llama, DeepSeek) бесплатны.\nОни ставятся на твой личный сервер.",
        "prompt": "A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Cyberpunk neon city background, cinematic."
    },
    {
        "headline": "ПИШИ СЛОВО:\nОТКРЫТЫЙ",
        "subtext": "Пиши мне в Директ кодовое слово,\nи я скину мануал по запуску ИИ.",
        "prompt": "A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Cinematic, highly detailed, moody."
    }
]

out_dir = "/Users/higherpower/.gemini/antigravity/brain/c1edc89f-b82d-476c-8418-be8adaaf40a4/carousel_output"
os.makedirs(out_dir, exist_ok=True)

# Helper function to add watermark
def add_watermark(img_path):
    img = Image.open(img_path).convert("RGBA")
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
    
    out = Image.alpha_composite(img, txt_layer)
    out.convert("RGB").save(img_path)

# Helper function to add text
def draw_text_on_image(img_path, headline, subtext):
    img = Image.open(img_path).convert("RGBA")
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
    
    out = Image.alpha_composite(img, txt_layer)
    out.convert("RGB").save(img_path)

generated_files = []

for i, slide in enumerate(slides):
    idx = i + 1
    print(f"Генерация слайда {idx}/6...")
    try:
        # Vertex has a quota of 2 requests per minute. We add sleep to avoid errors.
        if i > 0 and i % 2 == 0:
            print("Пауза 35 секунд из-за лимитов Vertex AI...")
            time.sleep(35)
            
        images = model.generate_images(
            prompt=slide["prompt"],
            number_of_images=1,
            aspect_ratio="3:4"
        )
        out_path = os.path.join(out_dir, f"final_slide_{idx}.png")
        images[0].save(location=out_path)
        
        draw_text_on_image(out_path, slide["headline"], slide["subtext"])
        add_watermark(out_path)
        generated_files.append(out_path)
        print(f"✅ Слайд {idx} сохранен.")
    except Exception as e:
        print(f"Ошибка на слайде {idx}: {e}")

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
