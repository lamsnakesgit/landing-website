import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

out_path = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip7_start_panic.png"
prompt = 'Gritty 90s anime style, cyberpunk anime. A panicked young developer typing frantically on a mechanical keyboard. Red binary code and error messages reflect vividly in his round glasses. Fast-paced hacking scene.'

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
        with open(out_path, "wb") as f:
            f.write(generated_image.image.image_bytes)
except:
    pass
