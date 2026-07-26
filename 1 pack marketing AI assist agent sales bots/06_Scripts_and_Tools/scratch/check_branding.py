# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()
    
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    local_video = "04_Design_and_Media/spy_downloads/kaisar_reel.mp4"
    with open(local_video, "rb") as f:
        video_bytes = f.read()
        
    prompt = (
        "Проверь это видео kaisar_reel.mp4. Есть ли на нем водяные знаки (watermarks), логотипы, юзернеймы "
        "(например, @kaisar_... или подобные), упоминания имени 'Кайсар' или его лицо в B-roll фрагментах?\n"
        "Укажи конкретные таймкоды и опиши, где именно они находятся, чтобы мы могли их убрать или замазать."
    )
    
    video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_part, prompt]
        )
        print("\n=== АНАЛИЗ НАЛИЧИЯ БРЕНДИНГА КАЙСАРА ===")
        print(response.text)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
