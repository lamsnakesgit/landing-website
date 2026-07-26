import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"

try:
    client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")
except Exception as e:
    print(f"Ошибка инициализации клиента: {e}")
    sys.exit(1)

def generate_image(prompt, output_filename):
    print(f"Генерация {output_filename}...")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
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
            return True
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return False

# Подробный промпт на основе истинного лица (молодая девушка, азиатка/казашка)
prompt = (
    "A photorealistic vertical close-up portrait of a young adult Central Asian / Kazakh woman in her early 20s. "
    "She has a soft oval face, very smooth clear skin with warm undertones, and dark brown almond-shaped eyes with a subtle epicanthic fold. "
    "Her eyebrows are naturally dark, straight, and neat. Her nose is small and straight. "
    "Her lips are natural light pinkish-rose, medium fullness, closed in a calm neutral expression. "
    "She has a clean white towel wrapped around her head, and she is wearing a soft cozy white bathrobe. "
    "The background is a bright, modern bathroom or spa with soft studio lighting. "
    "High-end fashion photography, 8k resolution, vertical 9:16 aspect ratio."
)

out_path1 = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/04_Design_and_Media/photo_shoot/15.png"
out_path2 = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/04_Design_and_Media/photo_session_portfolio/photo session portfolio me /photo_15_bathrobe_towel.png"

success = generate_image(prompt, out_path1)
if success:
    import shutil
    shutil.copy(out_path1, out_path2)
    print("Успешно скопировано во второй каталог!")
