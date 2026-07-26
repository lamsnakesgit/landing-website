import os
from PIL import Image, ImageDraw, ImageFont

# Папка с нашими чистыми картинками
base_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/version_cinematic"

def add_overlays_scene2():
    print("Overlaying Scene 2 (Mansur laptop labels)...")
    img_path = os.path.join(base_dir, "scene2_mansur_clean.png")
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found")
        return
        
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    
    # Поскольку координаты крышки ноутбука зависят от генерации, мы нарисуем стильный полупрозрачный
    # плашковый оверлей в углу кадра (или водяной знак), чтобы гарантировать 100% читаемость ников.
    # Создаем плашку внизу кадра
    width, height = img.size
    
    # Нарисуем плашку
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlay)
    
    # Прямоугольник для текста (черный полупрозрачный)
    ol_draw.rectangle([0, height - 120, width, height], fill=(0, 0, 0, 160))
    
    # Объединяем картинку и оверлей
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)
    
    # Пишем ники
    try:
        # Используем дефолтный шрифт
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((20, height - 100), "TG: @nnsvt   |   INST: @lamanopro_", fill=(255, 255, 255, 255), font=font)
    
    out_path = os.path.join(base_dir, "scene2_mansur_final.png")
    img.convert('RGB').save(out_path)
    print(f"Saved Scene 2 final: {out_path}")

def add_overlays_scene3():
    print("Overlaying Scene 3 (Kaspi & Telegram SMS)...")
    img_path = os.path.join(base_dir, "scene3_phone_clean.png")
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found")
        return
        
    img = Image.open(img_path)
    width, height = img.size
    
    # Создаем оверлей
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlay)
    
    # Рисуем плашку Kaspi (красный округлый прямоугольник)
    # Центрируем по ширине экрана
    card_w = int(width * 0.9)
    card_h = 130
    x0 = int((width - card_w) / 2)
    y0 = int(height * 0.3)
    
    # Kaspi уведомление (красная плашка)
    ol_draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + card_h], radius=15, fill=(212, 18, 36, 230))
    
    # Telegram СМС (сине-серая плашка чуть ниже)
    y1 = y0 + card_h + 30
    ol_draw.rounded_rectangle([x0, y1, x0 + card_w, y1 + card_h + 20], radius=15, fill=(40, 50, 65, 230))
    
    # Объединяем
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)
    
    # Пишем текст
    # 1. Текст Kaspi
    draw.text((x0 + 20, y0 + 20), "Kaspi.kz", fill=(255, 255, 255, 255))
    draw.text((x0 + 20, y0 + 60), "Пополнение: +1,500,000 KZT", fill=(255, 255, 255, 255))
    
    # 2. Текст Telegram
    draw.text((x0 + 20, y1 + 20), "Telegram: Баке", fill=(100, 180, 240, 255))
    draw.text((x0 + 20, y1 + 60), "Мансик, твой бот выбил долг за 3 мин!", fill=(255, 255, 255, 255))
    draw.text((x0 + 20, y1 + 90), "Но наш сервер взломали...", fill=(255, 100, 100, 255))
    
    # Добавляем водяной знак @aiconicvibe
    draw.text((width - 150, 30), "@aiconicvibe", fill=(255, 255, 255, 120))
    
    out_path = os.path.join(base_dir, "scene3_phone_final.png")
    img.convert('RGB').save(out_path)
    print(f"Saved Scene 3 final: {out_path}")

if __name__ == "__main__":
    add_overlays_scene2()
    add_overlays_scene3()
