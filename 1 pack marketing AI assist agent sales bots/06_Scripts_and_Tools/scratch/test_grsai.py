import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GRSAI_KEY = os.getenv("GRSAI_API_KEY")
if not GRSAI_KEY:
    print("GRSAI_API_KEY не задан в .env")
    exit(1)

base_url = "https://api.grsai.com/v1"
client = OpenAI(api_key=GRSAI_KEY, base_url=base_url)

print("1. Запрашиваем список доступных моделей...")
try:
    models = client.models.list()
    print("Доступные модели:")
    for m in models.data:
        print(f"  - {m.id}")
except Exception as e:
    print(f"Ошибка получения списка моделей: {e}")

print("\n2. Тестируем конкретные модели...")
models_to_try = ["claude-sonnet-4-6", "claude-3-5-sonnet", "gpt-4o", "nano-banana-2"]
for model in models_to_try:
    print(f"Пробуем модель {model}...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Привет! Ответь кратко 'Привет от Gemini/Claude!'"}],
            max_tokens=20
        )
        print(f"  ✅ Успех для {model}: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"  ❌ Ошибка для {model}: {e}")
