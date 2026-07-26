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

model_name = "veo-3.1-generate-001"
output_dir = "/Users/higherpower/.gemini/antigravity/brain/a1900323-aa8f-462f-b784-aa76fcc255ef"

slides = [
    {
        "id": "slide4",
        "prompt": "Vertical 9:16 video. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Cyberpunk, high contrast, cinematic lighting, symbol of rebellion. Photorealistic, 4k.",
        "output": os.path.join(output_dir, "slide4_veo.mp4")
    },
    {
        "id": "slide5",
        "prompt": "Vertical 9:16 video. An open source rebel hero proudly holding a glowing open source license in a rainy neon-lit city. Surrounding him are digital chains breaking apart. Powerful, inspiring, cyberpunk aesthetics, cinematic action. Photorealistic.",
        "output": os.path.join(output_dir, "slide5_veo.mp4")
    },
    {
        "id": "slide6",
        "prompt": "Vertical 9:16 video. Extreme close up of a glowing futuristic digital subscribe button in a dark hacker room. The button is pulsing with intense neon red and blue energy, ready to be pressed. High tension, high contrast, epic cinematic shot, 4k.",
        "output": os.path.join(output_dir, "slide6_veo.mp4")
    }
]

for slide in slides:
    print(f"Запуск генерации {slide['id']} через Veo...")
    try:
        operation = client.models.generate_videos(
            model=model_name,
            prompt=slide['prompt'],
            config=types.GenerateVideosConfig(
                person_generation="ALLOW_ADULT",
                aspect_ratio="9:16",
                duration_seconds=8
            )
        )
        
        print("Ожидание завершения (это займет несколько минут)...")
        while not operation.done:
            time.sleep(10)
            print(".", end="", flush=True)
            operation = client.operations.get(operation)
        print()
        
        if operation.error:
            print(f"Ошибка генерации {slide['id']}: {operation.error}")
        elif operation.result and operation.result.generated_videos:
            video_obj = operation.result.generated_videos[0].video
            if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                with open(slide['output'], "wb") as f:
                    f.write(video_obj.video_bytes)
                print(f"Видео успешно сохранено: {slide['output']}")
        else:
            print(f"Видео не было сгенерировано для {slide['id']}")
    except Exception as e:
        print(f"Ошибка при обработке {slide['id']}: {e}")
