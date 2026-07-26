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
    model = GenerativeModel("gemini-1.0-pro")
    
    response = model.generate_content("Тест")
    print("=== ОТВЕТ ОТ VERTEX AI GEMINI 1.0 PRO ===")
    print(response.text.strip())
except Exception as e:
    print(f"Error calling Vertex AI: {e}")

