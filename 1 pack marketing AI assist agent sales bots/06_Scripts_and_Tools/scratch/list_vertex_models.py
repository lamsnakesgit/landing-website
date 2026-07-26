# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv()
    
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    
    print("Инициализация клиента Vertex AI...")
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    print("Список моделей на Vertex AI:")
    try:
        # Пытаемся получить список моделей
        for model in client.models.list():
            print(f"- {model.name} (поддерживает: {model.supported_actions})")
    except Exception as e:
        print("Ошибка при получении списка моделей:", str(e))

if __name__ == "__main__":
    main()
