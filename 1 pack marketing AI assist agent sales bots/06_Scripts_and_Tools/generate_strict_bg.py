import os
import json
import requests
import base64
import time
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

files = ["wednesday", "sprunki", "brainrot", "mermaid"]

for name in files:
    print(f"Processing {name}...")
    try:
        with open(f"маркет_мобил_приложений/avatarworld/original_screens/{name}.png", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Skipping {name}, file not found")
        continue

    prompt = (
        "Expand the image into a perfect square format (1:1 ratio) suitable for an app icon. "
        "CRITICAL REQUIREMENT: KEEP THE MAIN CHARACTER AND FOREGROUND EXACTLY 100% UNCHANGED. Do not alter the face, pose, clothes, or style of the original character in any way. "
        "ONLY change and expand the BACKGROUND. Make the background a vibrant, bright, pastel 'Avatar World' mobile game style background (cute, 2D vector, cartoonish environment). "
        "Remove any UI elements or buttons from the background."
    )

    payload = {
        "contents": [{"role": "user", "parts": [
            {"inlineData": {"mimeType": "image/png", "data": img_b64}},
            {"text": prompt}
        ]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "temperature": 0.1 # Low temperature to minimize changes to the original character
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            out_b64 = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
            out_bytes = base64.b64decode(out_b64)
            with open(f"маркет_мобил_приложений/avatarworld/generated_bg/out_strict_{name}.png", "wb") as f:
                f.write(out_bytes)
            print(f"Saved out_strict_{name}.png")
        except KeyError:
            print(f"Failed to get image for {name}: {data}")
    else:
        print(f"Error {response.status_code}: {response.text}")
    print("Sleeping for 25 seconds to avoid rate limit...")
    time.sleep(25)
