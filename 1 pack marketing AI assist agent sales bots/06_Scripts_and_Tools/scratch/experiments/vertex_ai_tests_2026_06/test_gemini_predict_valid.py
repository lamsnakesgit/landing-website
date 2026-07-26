import os, requests, google.auth
from google.auth.transport.requests import Request
import base64

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

model = "gemini-3.1-flash-image"
loc = "us-central1"
url = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model}:predict"
headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}

payload = {
    "instances": [
        {
            "prompt": "A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay exactly reads: \"СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ\". Cyberpunk, high contrast, symbol of rebellion."
        }
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "3:4",
        "outputMimeType": "image/png"
    }
}

print("Sending valid predict request to gemini-3.1-flash-image...")
res = requests.post(url, headers=headers, json=payload)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    print("SUCCESS!")
    response_json = res.json()
    predictions = response_json.get("predictions", [])
    if predictions:
        # Save image
        img_b64 = predictions[0].get("bytesBase64Encoded")
        if img_b64:
            img_data = base64.b64decode(img_b64)
            with open("test_flash_image.png", "wb") as f:
                f.write(img_data)
            print("Saved to test_flash_image.png")
else:
    print(res.text[:1000])

print("\nTesting gemini-3.1-pro-image...")
model_pro = "gemini-3.1-pro-image"
url_pro = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model_pro}:predict"
res_pro = requests.post(url_pro, headers=headers, json=payload)
print(f"Status Code Pro: {res_pro.status_code}")
if res_pro.status_code == 200:
    print("SUCCESS PRO!")
    predictions = res_pro.json().get("predictions", [])
    if predictions:
        img_b64 = predictions[0].get("bytesBase64Encoded")
        if img_b64:
            img_data = base64.b64decode(img_b64)
            with open("test_pro_image.png", "wb") as f:
                f.write(img_data)
            print("Saved to test_pro_image.png")
else:
    print(res_pro.text[:1000])
