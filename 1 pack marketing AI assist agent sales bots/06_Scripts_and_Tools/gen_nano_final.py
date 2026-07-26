import os
import json
import requests
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def generate():
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
    
    # Read the NEWEST image (the one with 'АВТОНОМНЫЕ АГЕНТЫ')
    image_path = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/media__1784922984008.jpg"
    with open(image_path, "rb") as f:
        img_data = f.read()
    b64_img = base64.b64encode(img_data).decode('utf-8')
    
    prompt = """This is an image-to-image editing task.
I want you to keep the EXACT same image, but ONLY change the text inside the bottom cyan glowing banner.
Change the text inside the cyan banner to exactly read: "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН | ВХОД ПО ЗАПИСИ".
Do NOT change the girl, the robots, the background, the main title, the bullet points, or the logos at the very bottom. Keep everything else strictly identical."""
    
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
        try:
            b64_out = None
            for candidate in data.get('candidates', []):
                for part in candidate.get('content', {}).get('parts', []):
                    if 'inlineData' in part:
                        b64_out = part['inlineData']['data']
                        break
            
            if b64_out:
                out_path = '/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/nano_final_edit_date.jpg'
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
    generate()
