import os
import sys
import threading
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации: {e}")
    sys.exit(1)

scenes = [
    {
        "id": "clip6_start_hacked.png",
        "prompt": 'Gritty 90s anime style, dark thriller anime. A laptop screen suddenly turns bright red with warning popups. The camera cuts to the two characters whose faces instantly turn to pure terror. Dramatic red lighting. The laptop screen displays bold English text: "HACKED".'
    },
    {
        "id": "clip7_start_panic.png",
        "prompt": 'Gritty 90s anime style, cyberpunk anime. A panicked young developer typing frantically on a mechanical keyboard. Red binary code and error messages reflect vividly in his round glasses. Fast-paced hacking scene.'
    },
    {
        "id": "clip8_start_sparks.png",
        "prompt": 'Gritty 90s anime style, dramatic anime style. A laptop screen violently short-circuits with sparks flying, then the screen dies completely. The entire garage plunges into total darkness. Fast camera pull back.'
    }
]

def generate_scene(scene):
    out_path = f"/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/{scene['id']}"
    print(f"Генерация {scene['id']}...")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=scene['prompt'],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="9:16"
            )
        )
        for generated_image in result.generated_images:
            with open(out_path, "wb") as f:
                f.write(generated_image.image.image_bytes)
            print(f"Успешно сохранено: {out_path}")
    except Exception as e:
        print(f"Ошибка для {scene['id']}: {e}")

threads = []
for s in scenes:
    t = threading.Thread(target=generate_scene, args=(s,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Все сцены завершены.")
