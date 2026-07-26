import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

models = ["gemini-3.1-flash-image", "gemini-3-pro-image", "gemini-3.1-flash-image-preview"]
locations = ["us-central1", "us-east4", "us-west1", "europe-west3", "europe-west4", "europe-west9", "asia-southeast1"]

payload = {
    "instances": [
        {
            "prompt": "A simple drawing of a yellow banana."
        }
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1"
    }
}

for loc in locations:
    for model in models:
        url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
        headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                print(f"SUCCESS: model={model} in region={loc}!")
            elif res.status_code != 404:
                print(f"STATUS {res.status_code}: model={model} in region={loc}. Response: {res.text[:200]}")
        except Exception as e:
            print(f"Failed {model} in {loc}: {e}")

print("Done testing all regions.")
