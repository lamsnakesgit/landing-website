import requests
import json
import base64

API_KEY = "sk-8EobYRv3Rxkh5FWiEc735e5e391948569f3269Cf6273A9Ac"
URL = "https://aihubmix.com/v1/images/generations"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

models_to_test = ["gemini-3.1-flash-image", "gpt-image-2", "gemini-3.1-flash-image-preview"]

for model in models_to_test:
    data = {
        "model": model,
        "prompt": "Cyberpunk hacker",
        "n": 1,
        "size": "1024x1024"
    }
    print(f"Testing {model}...")
    res = requests.post(URL, headers=headers, json=data)
    print(res.status_code)
    print(res.text)
