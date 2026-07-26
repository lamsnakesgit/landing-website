import requests
import os

api_key = "AQ.Ab8RN6K5ssAcNr8kU8asQysWhqtc8NiFNVevK-p_VDciOL3hfA" # From .env
model = "gemini-3.1-flash-image"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "A simple yellow banana"}
            ]
        }
    ],
    "generationConfig": {
        "responseModalities": ["IMAGE"]
    }
}

print(f"Testing {model} via AI Studio API Key...")
res = requests.post(url, json=payload)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    print("SUCCESS!")
    print(res.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].keys())
else:
    print(res.text[:500])

print("\nTesting gemini-3.1-pro-image (or gemini-3-pro-image) via AI Studio API Key...")
model_pro = "gemini-3.1-pro-image"
url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/{model_pro}:generateContent?key={api_key}"
res_pro = requests.post(url_pro, json=payload)
print(f"Status Code Pro: {res_pro.status_code}")
if res_pro.status_code == 200:
    print("SUCCESS PRO!")
else:
    # Try gemini-3-pro-image
    model_pro2 = "gemini-3-pro-image"
    url_pro2 = f"https://generativelanguage.googleapis.com/v1beta/models/{model_pro2}:generateContent?key={api_key}"
    res_pro2 = requests.post(url_pro2, json=payload)
    print(f"Status Code Pro2 ({model_pro2}): {res_pro2.status_code}")
    if res_pro2.status_code == 200:
        print("SUCCESS PRO2!")
    else:
        print(res_pro2.text[:500])

