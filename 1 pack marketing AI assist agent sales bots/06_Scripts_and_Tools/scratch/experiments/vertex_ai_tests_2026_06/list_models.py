import os
import google.auth
from google.auth.transport.requests import Request
import requests

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models"
headers = {"Authorization": f"Bearer {credentials.token}"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json().get('models', [])
    for m in models:
        name = m.get('name', '')
        if 'image' in name.lower() or 'gemini' in name.lower() or 'imagen' in name.lower() or 'nano' in name.lower():
            print(name)
else:
    print(response.status_code, response.text)
