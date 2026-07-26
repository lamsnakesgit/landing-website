import os
import json
import requests
import base64
from google.oauth2 import service_account
import google.auth.transport.requests

# Load SA
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

prompts = [
    ("wednesday", "Avatar World mobile game art style, a cute cartoon drawing of Wednesday Addams with black braids, pale skin, wearing a dark school uniform, purple background with a subtle spooky vibe, square, high quality"),
    ("mermaid", "Avatar World mobile game art style, a cute cartoon drawing of a mermaid tail diving into water, bright green and blue colors, square, high quality"),
    ("log", "Avatar World mobile game art style, a cute cartoon drawing of a brown cylindrical wooden log with a face, big eyes and a mouth, holding a smaller baby log with a green pacifier and a baby bottle, standing in a bright green cartoon forest, square, high quality"),
    ("sprunki", "Avatar World mobile game art style, a cute cartoon vintage desk scene with an old leather-bound book, an antique brass compass resting on it, square, high quality"),
    ("house", "Avatar World mobile game art style, a 2.5D isometric view of a modern two-story house with a slanted pink roof, wood accents, and a small green garden, bright sunny day, square, high quality"),
    ("city", "Avatar World mobile game art style, a 2.5D isometric view of modern flat-roof city buildings, one white with orange accents, another blue with yellow accents, green grass and trees around, bright sunny day, square, high quality"),
    ("coins", "Avatar World mobile game art style, a 2D cartoon pile of shiny green, teal, and purple casino chips or coins with a star on them, bright pink background with sparkles, text 'POPULAR 1250', square, high quality"),
    ("telescope", "Avatar World mobile game art style, a cute cartoon brass telescope on a wooden tripod, pointing towards a sunset over dark misty mountains, square, high quality")
]

for name, prompt in prompts:
    print(f"Generating {name}...")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "temperature": 1.0}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            img_b64 = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
            img_bytes = base64.b64decode(img_b64)
            with open(f"{name}_nano.png", "wb") as f:
                f.write(img_bytes)
            print(f"Saved {name}_nano.png")
        except KeyError:
            print(f"Failed to get image for {name}: {data}")
    else:
        print(f"Error {response.status_code}: {response.text}")
