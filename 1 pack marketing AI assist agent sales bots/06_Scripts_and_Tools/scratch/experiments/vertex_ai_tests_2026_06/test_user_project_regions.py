import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

print(f"Project ID from credentials: {PROJECT_ID}")

model_flash = "gemini-3.1-flash-image"
model_pro = "gemini-3.1-pro-image" # Let's test this for Nano Banana Pro too

locations = [
    "us-central1", "us-east4", "us-west1", "us-west4",
    "europe-west1", "europe-west2", "europe-west3", "europe-west4",
    "europe-west9", "asia-southeast1", "asia-northeast1", "asia-northeast3",
    "global"
]

for loc in locations:
    headers = {'Authorization': f'Bearer {credentials.token}', 'Content-Type': 'application/json'}
    
    # Test Flash Predict
    url_predict_flash = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model_flash}:predict"
    res = requests.post(url_predict_flash, headers=headers, json={})
    if res.status_code != 404:
         print(f"FLASH {loc} predict: {res.status_code}")
         
    # Test Pro Predict
    url_predict_pro = f"https://{loc}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/{model_pro}:predict"
    res = requests.post(url_predict_pro, headers=headers, json={})
    if res.status_code != 404:
         print(f"PRO {loc} predict: {res.status_code}")

print("Done")
