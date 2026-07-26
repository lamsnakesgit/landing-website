import os
import sys
import json
import requests
import google.auth
import google.auth.transport.requests

def log(msg):
    print(msg, flush=True)

# Загружаем учетные данные из GOOGLE_APPLICATION_CREDENTIALS
try:
    credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token
    log("Auth token acquired successfully.")
except Exception as e:
    log(f"Failed to get auth token: {e}")
    sys.exit(1)

# Данные для запроса
payload = {
    "instances": [
        {
            "prompt": "3D Pixar style animation. A huge, muscular Kazakh man (Bake) in a black leather jacket, pointing his finger down aggressively. Post-soviet city courtyard, dramatic lighting."
        }
    ],
    "parameters": {
        "aspectRatio": "9:16",
        "durationSeconds": 5
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Попробуем эндпоинт Vertex AI
vertex_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/veo-2.0-generate-001:predictLongRunning"
log(f"Trying Vertex AI URL: {vertex_url}")

try:
    response = requests.post(vertex_url, json=payload, headers=headers, timeout=20)
    log(f"Vertex Response Status: {response.status_code}")
    log(f"Vertex Response Body: {response.text}")
except Exception as e:
    log(f"Vertex Request failed: {e}")

# Попробуем эндпоинт Gemini Developer API
gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/veo-2.0-generate-001:predictLongRunning"
log(f"Trying Gemini Developer URL: {gemini_url}")

try:
    response = requests.post(gemini_url, json=payload, headers=headers, timeout=20)
    log(f"Gemini Response Status: {response.status_code}")
    log(f"Gemini Response Body: {response.text}")
except Exception as e:
    log(f"Gemini Request failed: {e}")
