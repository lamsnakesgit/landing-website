import json
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel

try:
    with open('vertex_sa.json', 'r') as f:
        sa_info = json.load(f)
        project_id = sa_info.get('project_id')
except Exception as e:
    print(f"Error reading vertex_sa.json: {e}")
    exit(1)

try:
    credentials = service_account.Credentials.from_service_account_file('vertex_sa.json')
    vertexai.init(project=project_id, location='us-central1', credentials=credentials)
    
    # Пробуем новую модель Gemini 3.5 Flash
    model = GenerativeModel("gemini-3.5-flash")
    response = model.generate_content("Скажи одно слово: Работает")
    print("=== ОТВЕТ ОТ GEMINI 3.5 FLASH ===")
    print(response.text.strip())
except Exception as e:
    print(f"Error with 3.5 Flash: {e}")

