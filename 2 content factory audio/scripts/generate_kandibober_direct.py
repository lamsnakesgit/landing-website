import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корень проекта в path, чтобы импортировать core
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.nano_banana_generator import generate_story_image

def main():
    load_dotenv(BASE_DIR / ".env")
    
    # Текст для мема
    meme_text = "ИМЯ МОЁ ВАМ НИЧЕГО НЕ СКАЖЕТ. А ВОТ ПОДПИСКА НА AI — СКАЖЕТ ВСЁ."
    contact_text = "t.me/nnsvt"
    
    slide = {
        "slide_number": 1,
        "stage": "Meme",
        "type": "photo",
        "source_image_path": str(BASE_DIR / "name_kandibober_photo_2026-04-12 02.17.19.jpeg"),
        "script_text": f"{meme_text}\n{contact_text}", # Передаем текст напрямую в модель
        "visual_prompt": (
            "STRICT IDENTITY PRESERVATION: The woman in this image MUST have the EXACT SAME FACE, features, and expression as the woman in the attached source photo. "
            "DO NOT alter her appearance, do not beautify her, do not change her age. She must be 100% recognizable as the woman from the original 'Kandibober' meme. "
            "She is wearing the same bright red large turban-like hat (kandibober). "
            "The background is a realistic city street. "
            "Add floating, glowing 3D logos of ChatGPT, Google Gemini, and Claude in the air around her. "
            "The overall image should look like a high-definition, cinematic version of the original meme, but her face must remain UNCHANGED. "
            f"The main text '{meme_text}' is written in large, bold, white meme-style letters with a black outline at the bottom of the image. "
            f"Below the main text, in a smaller but readable font, add the contact link: '{contact_text}'. "
            "The image aspect ratio is 1:1 square."
        ),
        "layout_instructions": f"Square 1:1 aspect ratio. Main text and contact link '{contact_text}' should be integrated into the image at the bottom. ABSOLUTE IDENTITY MATCH for the woman's face is required.",
        "audio_suggestion": ""
    }
    
    story_context = {
        "goal": "Create a viral AI meme",
        "strategy": "Humor and nostalgia",
        "audience": "AI enthusiasts",
        "style": "Cinematic realism, 1:1 square aspect ratio, integrated Russian text"
    }
    
    final_output = BASE_DIR / "outputs" / "kandibober_direct_banana.png"
    
    print("Generating meme directly with Nano Banana Pro (1:1)...")
    try:
        # Мы используем существующую функцию, но Nano Banana Pro обычно подстраивается под промпт.
        # Если в core/nano_banana_generator.py жестко зашит 9:16, нам может понадобиться небольшая правка,
        # но обычно модель слушается текстовых инструкций про 1:1.
        result = generate_story_image(slide, final_output, story_context=story_context)
        print(f"✅ Мем сгенерирован напрямую: {result['file_path']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
