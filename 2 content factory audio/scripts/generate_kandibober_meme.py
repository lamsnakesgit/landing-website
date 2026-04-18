import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Добавляем корень проекта в path, чтобы импортировать core
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.nano_banana_generator import generate_story_image

def add_meme_text(image_path, text, output_path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Попробуем найти подходящий шрифт (Impact часто используется для мемов)
    font_paths = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]
    
    font = None
    font_size = int(height * 0.06)
    for fp in font_paths:
        if Path(fp).exists():
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()

    # Разбиваем текст на две строки для лучшего вида
    lines = ["ИМЯ МОЁ ВАМ НИЧЕГО НЕ СКАЖЕТ.", "А ВОТ ПОДПИСКА НА AI — СКАЖЕТ ВСЁ."]
    
    y_text = height - int(height * 0.15)
    for line in lines:
        # Получаем размер текста через bbox
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        x = (width - w) / 2
        
        # Рисуем обводку (черную)
        outline_range = 3
        for adj in range(-outline_range, outline_range + 1):
            for adj2 in range(-outline_range, outline_range + 1):
                draw.text((x + adj, y_text + adj2), line, font=font, fill="black")
        
        # Рисуем основной текст (белый)
        draw.text((x, y_text), line, font=font, fill="white")
        y_text += h + 10

    img.save(output_path)
    print(f"✅ Мем с текстом сохранен: {output_path}")

def main():
    load_dotenv(BASE_DIR / ".env")
    
    # Путь к исходному изображению (которое прислал пользователь)
    # В контексте задачи оно должно быть доступно. Если нет - сгенерируем с нуля по описанию.
    # Но лучше использовать его как референс.
    
    slide = {
        "slide_number": 1,
        "stage": "Meme",
        "type": "photo",
        "script_text": "", # Текст наложим сами для контроля качества
        "visual_prompt": (
            "A high-quality cinematic recreation of the 'Woman in a Kandibober' meme. "
            "A middle-aged woman with a serious, intense expression wearing a bright red large turban-like hat (kandibober). "
            "She is on a city street background. "
            "Surrounded by floating, glowing 3D logos of ChatGPT, Google Gemini, and Claude. "
            "Cinematic lighting, 2K resolution, authentic meme vibe, sharp focus."
        ),
        "layout_instructions": "Leave the bottom 20% of the image clear for text overlay.",
        "audio_suggestion": ""
    }
    
    story_context = {
        "goal": "Create a viral AI meme",
        "strategy": "Humor and nostalgia",
        "audience": "AI enthusiasts",
        "style": "Cinematic realism mixed with meme aesthetics"
    }
    
    temp_output = BASE_DIR / "outputs" / "kandibober_base.png"
    final_output = BASE_DIR / "outputs" / "kandibober_ai_meme.png"
    
    print("Generating base image with Nano Banana Pro...")
    try:
        result = generate_story_image(slide, temp_output, story_context=story_context)
        print(f"Base image generated: {result['file_path']}")
        
        print("Adding meme typography...")
        add_meme_text(result['file_path'], "", final_output)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
