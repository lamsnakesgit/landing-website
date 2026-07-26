import os, requests, google.auth
from google.auth.transport.requests import Request

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())

model = "gemini-3-pro-image"
url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/publishers/google/models/{model}:generateContent"
headers = {
    'Authorization': f'Bearer {credentials.token}',
    'Content-Type': 'application/json',
}
payload = {
    'contents': [{'role': 'user', 'parts': [{'text': 'A simple yellow banana'}]}],
    'generationConfig': {
        'responseModalities': ['TEXT', 'IMAGE'],
        'temperature': 1.0,
    },
}

print(f"Testing {model} in global...")
res = requests.post(url, json=payload, headers=headers)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    print("SUCCESS PRO!")
else:
    print(res.text[:500])
