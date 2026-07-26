import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"

try:
    print("Инициализация Vertex AI клиента...")
    client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")
    
    prompt = (
        "A futuristic high-tech abstract background with neon cyan and purple glows, "
        "faint digital charts and neural network connections, ultra premium, clean, "
        "dark mode theme, 8k resolution, cinematic lighting, sleek design, wallpaper"
    )
    
    print(f"Генерация изображения по промпту: {prompt}")
    
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            output_mime_type="image/png"
        )
    )
    
    print("Изображение успешно сгенерировано. Сохранение...")
    os.makedirs("assets", exist_ok=True)
    
    for i, generated_image in enumerate(response.generated_images):
        output_path = "assets/bg_offer.png"
        # У объекта image есть байты
        image_bytes = generated_image.image.image_bytes
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Сохранено в {output_path}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
