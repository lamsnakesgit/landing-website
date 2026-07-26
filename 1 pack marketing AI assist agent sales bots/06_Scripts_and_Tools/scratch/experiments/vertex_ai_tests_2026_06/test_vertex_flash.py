import json
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel

try:
    with open('vertex_sa.json', 'r') as f:
        sa_info = json.load(f)
        project_id = sa_info.get('project_id')
except Exception as e:
    print(f"Error: {e}")
    exit(1)

try:
    credentials = service_account.Credentials.from_service_account_file('vertex_sa.json')
    vertexai.init(project=project_id, location='us-central1', credentials=credentials)
    
    # Пробуем самую легкую и доступную модель - Flash
    model = GenerativeModel("gemini-1.5-flash-001")
    response = model.generate_content("Напиши слово 'Работает'")
    print("Ответ от gemini-1.5-flash-001:", response.text.strip())
    
except Exception as e:
    print(f"Ошибка вызова: {e}")
