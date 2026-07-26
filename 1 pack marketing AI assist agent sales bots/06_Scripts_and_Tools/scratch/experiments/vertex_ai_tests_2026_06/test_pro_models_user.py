import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

models = ["gemini-3-pro-image", "gemini-3.1-pro-image", "gemini-3.1-pro-image-preview", "gemini-3.1-flash-image"]
loc = "us-central1"

payload = {
    "instances": [
        {"prompt": "A simple yellow banana"}
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1"
    }
}

for model in models:
    url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
    headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
    res = requests.post(url, headers=headers, json=payload)
    print(f"Model {model}: code={res.status_code}")
    if res.status_code == 200:
        print(f"-> SUCCESS for {model}!")
    elif res.status_code != 404:
        print(res.text[:200])
