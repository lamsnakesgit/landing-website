from PIL import Image, ImageDraw, ImageFont

img_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_start_anime.png"
out_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_text_overlay.png"

try:
    img = Image.open(img_path)
    d = ImageDraw.Draw(img)
    
    # Пытаемся загрузить красивый жирный шрифт, если нет - берем дефолтный
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 80)
    except:
        font = ImageFont.load_default()

    # Рисуем текст по центру
    text = "ВЫПОЛНИТЬ"
    
    # В новых версиях Pillow textsize устарел, используем textbbox
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (img.width - text_w) / 2
    y = (img.height - text_h) / 2
    
    # Добавляем черную обводку для читаемости (эффект тени/свечения)
    d.text((x-2, y-2), text, font=font, fill="black")
    d.text((x+2, y+2), text, font=font, fill="black")
    d.text((x, y), text, font=font, fill=(0, 255, 0)) # Зеленый текст
    
    img.save(out_path)
    print(f"Текст успешно наложен: {out_path}")
except Exception as e:
    print(f"Ошибка: {e}")
