import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Проверяем оба ключа
keys_to_test = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
}

for name, key in keys_to_test.items():
    if not key:
        print(f"Ключ {name} не найден в .env")
        continue
        
    print(f"\n--- Тестируем {name} ({key[:10]}...) ---")
    try:
        # Для google-genai SDK
        client = genai.Client(api_key=key)
        
        # Пробуем сделать простой запрос
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Привет, скажи кратко "Привет от Gemini!"',
        )
        print(f"Успех! Ответ: {response.text.strip()}")
        
        # Проверим поддержку JSON Schema / Structured Output
        print("Тестируем генерацию структурированного JSON...")
        
        class TestSchema:
            greeting: str
            confidence: int

        json_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Сгенерируй JSON с приветствием и уверенностью 100',
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TestSchema
            )
        )
        print(f"JSON Успех! Ответ: {json_response.text.strip()}")
        
    except Exception as e:
        print(f"Ошибка для {name}: {e}")
