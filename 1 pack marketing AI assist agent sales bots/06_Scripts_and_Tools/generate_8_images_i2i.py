import os
import json
import requests
import base64
from google.oauth2 import service_account
import google.auth.transport.requests

creds = service_account.Credentials.from_service_account_file(
    'vertex_sa.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

project_id = creds.project_id
url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/gemini-3.1-flash-image:generateContent"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

files = ["wednesday", "mermaid", "brainrot", "sprunki", "house", "city", "coins", "kpop_demon"]

for name in files:
    print(f"Processing {name}...")
    try:
        with open(f"source_images/{name}.png", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Skipping {name}, file not found")
        continue

    prompt = (
        "Recreate this exact image as a perfect square high-quality Avatar World mobile game art style background. "
        "Expand the background seamlessly to fit a square format. Remove any UI elements, text, buttons, or badges. "
        "Keep the main characters, objects, and overall art style identical to the reference. "
        "Bright pastel colors, flat 2D vector style, cute aesthetics."
    )

    payload = {
        "contents": [{"role": "user", "parts": [
            {"inlineData": {"mimeType": "image/png", "data": img_b64}},
            {"text": prompt}
        ]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "temperature": 0.5
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            out_b64 = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
            out_bytes = base64.b64decode(out_b64)
            with open(f"out_{name}.png", "wb") as f:
                f.write(out_bytes)
            print(f"Saved out_{name}.png")
        except KeyError:
            print(f"Failed to get image for {name}: {data}")
    else:
        print(f"Error {response.status_code}: {response.text}")
