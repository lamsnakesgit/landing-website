import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации: {e}")
    sys.exit(1)

output_dir = "/Users/higherpower/.gemini/antigravity/brain/a1900323-aa8f-462f-b784-aa76fcc255ef"

slides = [
    {
        "id": "slide4",
        "prompt": 'A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay exactly reads: "СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ". Cyberpunk, high contrast, symbol of rebellion.',
        "output": os.path.join(output_dir, "slide4_nanobanana.png")
    },
    {
        "id": "slide5",
        "prompt": 'An open source rebel hero proudly holding a glowing open source license in a rainy neon-lit city. Surrounding him are digital chains breaking apart. Big bold typography text overlay exactly reads: "OPEN SOURCE МОДЕЛИ". Powerful, inspiring, cyberpunk aesthetics.',
        "output": os.path.join(output_dir, "slide5_nanobanana.png")
    },
    {
        "id": "slide6",
        "prompt": 'Extreme close up of a glowing futuristic digital subscribe button in a dark hacker room. The button is pulsing with intense neon red and blue energy, ready to be pressed. Big bold typography text overlay exactly reads: "НАЧНИ СВОЙ ПУТЬ". High tension, epic cinematic shot.',
        "output": os.path.join(output_dir, "slide6_nanobanana.png")
    }
]

for slide in slides:
    print(f"Генерация {slide['id']} через Nano Banana 2 (gemini-3.1-flash-image)...")
    try:
        result = client.models.generate_images(
            model='gemini-3.1-flash-image',
            prompt=slide['prompt'],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="3:4"
            )
        )
        for generated_image in result.generated_images:
            with open(slide['output'], "wb") as f:
                f.write(generated_image.image.image_bytes)
            print(f"Сохранено: {slide['output']}")
    except Exception as e:
        print(f"Ошибка при обработке {slide['id']}: {e}")
