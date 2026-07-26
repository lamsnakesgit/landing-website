import os, requests, google.auth
from google.auth.transport.requests import Request
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

model = "gemini-3.1-flash-image"
loc = "us-central1"
url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}

# Let's see the error message for 400
res = requests.post(url, headers=headers, json={})
print(res.text)
