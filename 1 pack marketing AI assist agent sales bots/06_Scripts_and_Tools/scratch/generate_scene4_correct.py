import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
out_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_correct_start.png"

prompt = 'Gritty 90s anime style, thriller anime. Two young guys in a dark, messy garage. One looks hopeful, asking a question. The other developer is sitting at a computer, intensely pressing the ENTER key on a mechanical keyboard to launch a program. Cool blue and green screen glow reflecting on their faces. Cinematic lighting.'

try:
    res = client.models.generate_images(
        model='imagen-3.0-generate-001', prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/png", aspect_ratio="9:16")
    )
    with open(out_path, "wb") as f:
        f.write(res.generated_images[0].image.image_bytes)
    print("Успешно сохранено: " + out_path)
except Exception as e:
    print(f"Ошибка: {e}")
