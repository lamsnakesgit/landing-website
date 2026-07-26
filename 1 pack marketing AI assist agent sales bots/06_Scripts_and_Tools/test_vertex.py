import os
import json
import urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load credentials
creds = service_account.Credentials.from_service_account_file(
    'vertex_sa_trial.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
creds.refresh(Request())

project_id = 'my-project-13652-10-7-25-7n'
location = 'us-central1'
model = 'gemini-1.5-flash-001' # use a known valid model

url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"

data = {
    "contents": [{
        "role": "user",
        "parts": [{"text": "Hello"}]
    }]
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print("SUCCESS:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"ERROR: {str(e)}")
