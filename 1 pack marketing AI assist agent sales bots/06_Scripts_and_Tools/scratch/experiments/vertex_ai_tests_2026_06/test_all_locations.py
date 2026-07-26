import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

model = "gemini-3.1-flash-image"
locations = [
    "us-central1", "us-east4", "us-west1", "us-west4",
    "europe-west1", "europe-west2", "europe-west3", "europe-west4",
    "europe-west9", "asia-southeast1", "asia-northeast1", "asia-northeast3"
]

for loc in locations:
    url_predict = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
    url_generate = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:generateContent"
    headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
    
    # Test predict
    res1 = requests.post(url_predict, headers=headers, json={})
    if res1.status_code != 404:
        print(f"FOUND {loc} predict: {res1.status_code}")
        
    # Test generateContent
    res2 = requests.post(url_generate, headers=headers, json={})
    if res2.status_code != 404:
        print(f"FOUND {loc} generate: {res2.status_code}")
        
print("Done")
