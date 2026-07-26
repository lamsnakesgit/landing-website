import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

model = "gemini-3.1-flash-image"
loc = "global"
url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:generateContent"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}

payload = {
    "contents": [{"role": "user", "parts": [{"text": "A robot holding a sign saying HELLO WORLD"}]}],
    "generationConfig": {"responseModalities": ["IMAGE"]}
}

res = requests.post(url, headers=headers, json=payload)
print(f"Status Code for {loc} generateContent: {res.status_code}")
if res.status_code != 200:
    print(res.text[:500])
else:
    print("SUCCESS!")
    print(res.text[:100])
