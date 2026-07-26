import requests, google.auth
from google.auth.transport.requests import Request
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

url = f"https://us-central1-aiplatform.googleapis.com/v1/locations/us-central1/publishers/google/models"
headers = {'Authorization': f'Bearer {credentials.token}'}

res = requests.get(url, headers=headers)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    models = data.get("models", [])
    print(f"Total publisher models: {len(models)}")
    matches = []
    for m in models:
        name = m.get("name", "")
        # The name is usually like: publishers/google/models/gemini-1.5-flash-001
        if "gemini" in name or "image" in name or "banana" in name or "veo" in name:
            matches.append(name)
    print("Matches:")
    for match in matches:
        print(match)
else:
    print(res.text[:500])
