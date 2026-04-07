import asyncio
from pathlib import Path
from core.nano_banana_generator import generate_story_image

def test_banana():
    slide = {
        "slide_number": 1,
        "stage": "Hook",
        "type": "photo",
        "script_text": "Привет, это тест реализма!",
        "visual_prompt": "A person holding an iPhone, candid shot, natural lighting",
        "layout_instructions": "Text at the top",
        "audio_suggestion": "Chill lo-fi"
    }
    
    story_context = {
        "goal": "Test realism",
        "strategy": "Testing",
        "audience": "AI Agents",
        "style": "Candid iPhone photography"
    }
    
    output_path = Path("outputs/test_banana_realism.png")
    print(f"Generating image to {output_path}...")
    
    try:
        result = generate_story_image(slide, output_path, story_context=story_context)
        print(f"✅ Success! Image generated: {result['file_path']}")
        print(f"Prompt used: {result['prompt']}")
    except Exception as e:
        print(f"❌ Failure: {e}")

if __name__ == "__main__":
    test_banana()
