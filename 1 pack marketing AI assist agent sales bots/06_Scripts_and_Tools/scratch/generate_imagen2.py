import os
import sys
from google.cloud import aiplatform
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

vertexai.init(project="gen-lang-client-0675220826", location="us-central1")

try:
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    prompt = 'Gritty 90s anime style, cyberpunk anime. Macro close-up of a glowing computer screen showing a node-based visual programming interface (like n8n). A large green button glowing and pulsating. The screen features bold Russian text perfectly spelled: "ВЫПОЛНИТЬ".'
    
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="9:16"
    )
    
    output = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/clip4_start_imagen2.png"
    images[0].save(location=output)
    print(f"Сохранено: {output}")
except Exception as e:
    print(f"Ошибка: {e}")

