import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации клиента: {e}")
    sys.exit(1)

def generate_image(prompt, output_filename):
    print(f"Генерация {output_filename}...")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
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
        print(f"Ошибка генерации: {e}")

prompt4 = 'Gritty 90s anime style, cyberpunk anime. Macro close-up of a glowing computer screen showing a node-based visual programming interface. Wires connecting nodes quickly. A green button glowing and pulsating. The screen features bold Russian text: "ВЫПОЛНИТЬ".'
generate_image(prompt4, "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_start_anime.png")

prompt5 = 'Gritty 90s anime style. Close-up of a smartphone lying on a desk in a dark room. The screen lights up, showing a rapid stream of green popup transaction notifications. Vivid screen glow. The phone screen clearly displays Russian text: "KASPI ПЕРЕВОД" and "+100000".'
generate_image(prompt5, "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip5_start_anime.png")

prompt6 = 'Gritty 90s anime style, dark thriller anime. A laptop screen suddenly turns bright red with warning popups. Dramatic red lighting. The laptop screen displays bold Russian text: "ВЗЛОМ / ВНИМАНИЕ".'
generate_image(prompt6, "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip6_start_anime.png")

