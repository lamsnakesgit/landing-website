import os
import json
import requests
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def edit_image():
    creds = service_account.Credentials.from_service_account_file(
        'vertex_sa.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    creds.refresh(Request())
    token = creds.token
    project_id = 'my-project-97115-216-254'
    model_id = 'gemini-3.1-flash-image'
    
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/{model_id}:generateContent"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Read the original image
    image_path = "/Users/higherpower/Desktop/afisha_19_07.png"
    with open(image_path, "rb") as f:
        img_data = f.read()
    b64_img = base64.b64encode(img_data).decode('utf-8')
    
    prompt = """Recreate this exact poster but change the text on the bottom cyan banner.
Big bold typography text on the cyan banner exactly reads: "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН".
Do not change anything else. Keep the exact same Asian woman holding a coffee cup.
Keep the exact same logos at the bottom (Anthropic, Google AI, Claude, TG: @nnsvt).
Keep the exact same layout and cybernetic elements.
Square aspect ratio (1:1)."""
    
    payload = {
        "contents": [
            {
                "role": "user", 
                "parts": [
                    {"inlineData": {"mimeType": "image/png", "data": b64_img}},
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"]
        }
    }
    
    print("Sending request to Nano Banana 2 with original image...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        try:
            b64_out = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
            out_path = 'nano_banana_edited.jpg'
            with open(out_path, 'wb') as f:
                f.write(base64.b64decode(b64_out))
            print(f"Image saved as {out_path}")
        except Exception as e:
            print("Error parsing image data:", e)
            print(json.dumps(data, indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == '__main__':
    edit_image()
