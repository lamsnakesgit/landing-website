import os
import json
import requests
import google.auth
from google.auth.transport.requests import Request

# Указываем путь к твоему ключу
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"

try:
    credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(Request())
    
    # Эмулируем входящие данные (как будто спарсили компанию)
    company_name = "ТОО 'КазСтройЛес'"
    company_niche = "Оптовая продажа стройматериалов и пиломатериалов"
    target_lpr = "Иван"
    
    prompt = f"""
    Действуй как эксперт по холодным продажам. 
    Твоя задача — написать супер-персонализированное, короткое первое сообщение для WhatsApp.
    
    Данные лида:
    Компания: {company_name}
    Ниша: {company_niche}
    Имя ЛПР: {target_lpr}
    
    Наш оффер: Мы внедряем AI-систему лидогенерации, которая сама ищет строительные компании и прорабов, и пишет им персонализированные офферы, приводя теплых лидов без отдела продаж.
    
    Требования:
    - Пиши от лица Ильяса.
    - Максимум 3-4 предложения. Никакой воды.
    - Никаких "Здравствуйте, меня зовут". Сразу к сути и комплименту по их нише.
    - Сделай так, чтобы захотелось ответить.
    """
    
    # Исправленное имя модели
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/gemini-pro:generateContent"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.4
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        print("\n=== СГЕНЕРИРОВАННЫЙ ОФФЕР ===")
        print(text.strip())
        print("=============================")
    else:
        print(f"Ошибка API: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Ошибка: {e}")
