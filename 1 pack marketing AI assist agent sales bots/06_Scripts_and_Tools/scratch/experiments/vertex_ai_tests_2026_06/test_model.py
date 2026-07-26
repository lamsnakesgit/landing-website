import os, requests, google.auth
from google.auth.transport.requests import Request
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())
model = "gemini-3.1-flash-image"
LOCATION = "us-central1"
url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model}:generateContent"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
payload = {'contents': [{'role': 'user', 'parts': [{'text': 'A robot holding a sign saying HELLO'}]}], 'generationConfig': {'responseModalities': ['IMAGE']}}
r = requests.post(url, json=payload, headers=headers)
print(r.status_code)
print(r.text[:200])
