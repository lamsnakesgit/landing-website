import os, requests, google.auth
from google.auth.transport.requests import Request
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

models = ["gemini-3.1-flash-image", "gemini-3-pro-image", "gemini-2.5-flash-image", "imagen-3.0-generate-002"]
locations = ["us-central1", "us-east4", "europe-west1"]

for model in models:
    for loc in locations:
        url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:generateContent"
        if "imagen" in model:
            url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
            
        headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
        payload = {}
        if "imagen" in model:
             payload = {"instances": [{"prompt": "test"}], "parameters": {"sampleCount": 1}}
        else:
             payload = {'contents': [{'role': 'user', 'parts': [{'text': 'test'}]}], 'generationConfig': {'responseModalities': ['IMAGE']}}
        r = requests.post(url, json=payload, headers=headers)
        print(f"Model: {model}, Region: {loc}, Status: {r.status_code}")
