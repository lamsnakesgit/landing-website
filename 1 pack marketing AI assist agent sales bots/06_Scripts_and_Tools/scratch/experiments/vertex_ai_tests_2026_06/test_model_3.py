import os, requests, google.auth
from google.auth.transport.requests import Request
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())
model = "gemini-3.1-flash-image"
LOCATION = "us-central1"

# Test predict endpoint
url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model}:predict"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
payload = {
    "instances": [{"prompt": "A robot holding a sign saying HELLO"}],
    "parameters": {"sampleCount": 1}
}
r = requests.post(url, json=payload, headers=headers)
print("Predict endpoint status:", r.status_code)
print("Predict endpoint response:", r.text[:200])

