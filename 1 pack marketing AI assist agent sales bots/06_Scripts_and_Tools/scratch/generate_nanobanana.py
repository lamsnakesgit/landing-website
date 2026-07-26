import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации: {e}")
    sys.exit(1)

prompt = 'Gritty 90s anime style, cyberpunk anime. Macro close-up of a glowing computer screen showing a node-based visual programming interface (like n8n). A large green button glowing and pulsating. The screen features bold Russian text perfectly spelled: "ВЫПОЛНИТЬ".'

output_filename = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_nanobanana.png"
print(f"Генерация {output_filename} через Nano Banana 2 (gemini-3.1-flash-image)...")
try:
    result = client.models.generate_images(
        model='gemini-3.1-flash-image',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/png",
            aspect_ratio="9:16"
        )
    )
    for generated_image in result.generated_images:
        with open(output_filename, "wb") as f:
            f.write(generated_image.image.image_bytes)
        print(f"Сохранено: {output_filename}")
except Exception as e:
    print(f"Ошибка: {e}")

