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
        "Проверь видео kaisar_reel.mp4 очень внимательно.\n"
        "Составь список всех интервалов времени (таймкодов), в которых на экране ВИДЕН МУЖЧИНА (говорящий спикер, то есть Кайсар).\n"
        "Напиши точные секунды начала и конца для каждого фрагмента, где виден этот мужчина (даже если он виден частично, сбоку, со спины или его руки/тело).\n"
        "Мы хотим ПОЛНОСТЬЮ ИСКЛЮЧИТЬ его присутствие в нашем ролике. Нам нужны только чистые B-роллы без него."
    )
    
    video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_part, prompt]
        )
        print("\n=== ТАЙМКОДЫ С УЧАСТИЕМ МУЖЧИНЫ ===")
        print(response.text)
        
        # Запишем в файл
        with open("docs/kaisar_presence_timestamps.md", "w", encoding="utf-8") as f:
            f.write("# Таймкоды с присутствием мужчины в kaisar_reel.mp4\n\n")
            f.write(response.text)
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
