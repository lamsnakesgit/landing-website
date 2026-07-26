import os
import time
from google import genai
from google.genai import types

# Путь к JSON ключу на сервере
SA_KEY_PATH = os.path.join(os.path.dirname(__file__), "vertex_sa.json")
if os.path.exists(SA_KEY_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_KEY_PATH

# Project ID пользователя
PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"

def generate_veo_clip(text, image_path, output_path):
    print(f"[*] Запуск генерации Veo 3.1 Lite для текста: '{text}' на Vertex AI")
    
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        
        prompt_text = f"A highly detailed, photorealistic video of this person talking to the camera. They are saying: {text}"
        
        # Загружаем картинку
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        
        img = types.Image(image_bytes=img_bytes, mime_type="image/png" if image_path.endswith(".png") else "image/jpeg")
        ref_image = types.VideoGenerationReferenceImage(
            image=img,
            reference_type="ASSET"
        )
        
        response = client.models.generate_videos(
            model='veo-3.1-generate-001',
            prompt=prompt_text,
            config=types.GenerateVideosConfig(
                referenceImages=[ref_image]
            )
        )
        print("[!] Задача на генерацию отправлена. Ждем результата (это может занять несколько минут)...")
        
        op_name = response.name
        operation = response
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("Ожидание завершения генерации...")
            
        if operation.error:
            print(f"[-] Ошибка генерации: {operation.error}")
            return None
            
        for i, gen_video in enumerate(operation.result.generated_videos):
            with open(output_path, "wb") as f:
                f.write(gen_video.video.video_bytes)
            print(f"[+] Клип успешно сохранен в {output_path}")
            return output_path
            
    except Exception as e:
        print(f"[-] Исключение при вызове Vertex AI: {e}")
        
    return None

if __name__ == "__main__":
    generate_veo_clip("Тестовый запуск Veo Vertex AI", "studio_face.png", "veo_test.mp4")
