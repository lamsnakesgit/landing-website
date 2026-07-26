import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

loc = "us-central1"
# Totally fake model name
model = "this-is-a-completely-fake-model-banana-12345"
url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}

res = requests.post(url, headers=headers, json={})
print(f"Status Code for FAKE model predict with empty payload: {res.status_code}")
if res.status_code != 200:
    print(res.text[:300])

