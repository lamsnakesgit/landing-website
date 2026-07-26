import google.auth
from google.auth.transport.requests import Request
import requests
import json
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/vertex_sa.json"

credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

location = "us-central1"
# Trying imagen-3.0-generate-001
url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/imagen-3.0-generate-001:predict"

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; charset=utf-8"
}

data = {
    "instances": [
        {
            "prompt": "A cute ghost telegram sticker, clean background"
        }
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1"
    }
}

print("Project ID:", project_id)
response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)

if response.status_code == 200:
    res_json = response.json()
    if 'predictions' in res_json and len(res_json['predictions']) > 0:
        print("Success! Got predictions.")
    else:
        print("No predictions in response:", res_json)
else:
    print("Error:", response.text)
