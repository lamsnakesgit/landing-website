import os
import json
import urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

files_to_test = ["vertex_sa.json", "vertex_sa_crm.json", "vertex_sa_trial.json"]

for filename in files_to_test:
    print(f"\n=== Тестируем {filename} ===")
    if not os.path.exists(filename):
        print(f"Файл {filename} не существует в корне проекта.")
        continue
        
    try:
        with open(filename, "r") as f:
            sa_info = json.load(f)
            project_id = sa_info.get("project_id")
            
        print(f"Project ID: {project_id}")
        
        # Загружаем credentials
        creds = service_account.Credentials.from_service_account_file(
            filename,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        creds.refresh(Request())
        
        location = 'us-central1'
        # Попробуем как gemini-1.5-flash-001 так и gemini-2.5-flash
        model = 'gemini-1.5-flash-001' 
        
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"
        
        data = {
            "contents": [{
                "role": "user",
                "parts": [{"text": "Hello"}]
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
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ УСПЕХ! Ответ от {filename}: {result[:200]}...")
            
    except urllib.error.HTTPError as e:
        err_data = e.read().decode('utf-8')
        print(f"❌ HTTP ERROR {e.code} для {filename}: {err_data}")
    except Exception as e:
        print(f"❌ ОШИБКА для {filename}: {e}")
