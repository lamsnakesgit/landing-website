import google.auth
from google.auth.transport.requests import Request
import requests
import json
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

locations = ["us-central1", "us-east4", "europe-west1", "europe-west4", "us-west1", "asia-southeast1"]

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; charset=utf-8"
}

found_endpoints = []
for loc in locations:
    # List endpoints
    url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{loc}/endpoints"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        endpoints = res.json().get('endpoints', [])
        for ep in endpoints:
            print(f"Found Endpoint in {loc}: {ep['displayName']} (ID: {ep['name']})")
            found_endpoints.append(ep)
    
    # List models
    url_models = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{loc}/models"
    res_models = requests.get(url_models, headers=headers)
    if res_models.status_code == 200:
        models = res_models.json().get('models', [])
        for m in models:
            if 'nano' in m.get('displayName', '').lower() or 'banana' in m.get('displayName', '').lower():
                print(f"Found Nano Banana Model in {loc}: {m['displayName']} (ID: {m['name']})")

if not found_endpoints:
    print("No custom endpoints found.")
