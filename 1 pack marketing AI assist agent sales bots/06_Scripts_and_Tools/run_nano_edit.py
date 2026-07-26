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
    
    # Read the newest image
    image_path = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/media__1784922486205.jpg"
    with open(image_path, "rb") as f:
        img_data = f.read()
    b64_img = base64.b64encode(img_data).decode('utf-8')
    
    prompt = """Big bold typography text on the bottom cyan banner exactly reads: "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН".
Do not change anything else on the image. Keep the same Asian woman holding a coffee cup. Keep all the logos at the bottom exactly the same. Only the text on the cyan banner should change."""
    
    payload = {
        "contents": [
            {
                "role": "user", 
                "parts": [
                    {"inlineData": {"mimeType": "image/jpeg", "data": b64_img}},
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"]
        }
    }
    
    print("Sending request to Nano Banana 2...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        with open("nano_response.json", "w") as f:
            json.dump(data, f)
            
        print("Response saved to nano_response.json")
        try:
            # Let's try to extract image
            b64_out = None
            for candidate in data.get('candidates', []):
                for part in candidate.get('content', {}).get('parts', []):
                    if 'inlineData' in part:
                        b64_out = part['inlineData']['data']
                        break
            
            if b64_out:
                out_path = '/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/nano_edited_v2.jpg'
                with open(out_path, 'wb') as f:
                    f.write(base64.b64decode(b64_out))
                print(f"Image saved as {out_path}")
            else:
                print("No image found in response!")
        except Exception as e:
            print("Error parsing image data:", e)
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == '__main__':
    edit_image()
