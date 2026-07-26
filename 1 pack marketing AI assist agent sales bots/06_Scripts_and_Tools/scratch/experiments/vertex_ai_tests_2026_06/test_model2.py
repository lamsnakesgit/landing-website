import os, requests, google.auth
from google.auth.transport.requests import Request
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())
model = "imagen-3.0-generate-002"
LOCATION = "us-central1"
url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model}:predict"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
payload = {
    "instances": [{"prompt": "A robot holding a sign saying CLAUDE ЗАБАНИЛИ"}],
    "parameters": {"sampleCount": 1, "aspectRatio": "3:4"}
}
r = requests.post(url, json=payload, headers=headers)
print(r.status_code)
if r.status_code == 200:
    print("SUCCESS!")
else:
    print(r.text[:200])
