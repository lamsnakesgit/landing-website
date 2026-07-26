import os
import json
import urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

filename = "vertex_sa_crm.json"
if not os.path.exists(filename):
    print("vertex_sa_crm.json не найден")
    exit(1)

with open(filename, "r") as f:
    sa_info = json.load(f)
    project_id = sa_info.get("project_id")

print(f"Тестируем проект {project_id} с аккаунтом {filename}...")

creds = service_account.Credentials.from_service_account_file(
    filename,
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
creds.refresh(Request())

# Модели для тестирования в Vertex AI
models_to_test = [
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-002",
]

location = 'us-central1'

for model in models_to_test:
    print(f"\n--- Пробуем модель: {model} ---")
    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"
    
    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": "Привет, ответь одним коротким словом."}]
        }]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ УСПЕХ! Ответ от {model}: {result[:300]}...")
            # Если сработало, то отлично!
    except urllib.error.HTTPError as e:
        err_data = e.read().decode('utf-8')
        print(f"❌ HTTP ERROR {e.code} для {model}: {err_data[:500]}")
    except Exception as e:
        print(f"❌ ОШИБКА для {model}: {e}")
