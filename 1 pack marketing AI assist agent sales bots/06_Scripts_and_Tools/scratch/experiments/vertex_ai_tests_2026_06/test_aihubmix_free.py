import requests
import json
import base64

API_KEY = "sk-8EobYRv3Rxkh5FWiEc735e5e391948569f3269Cf6273A9Ac"
URL = "https://aihubmix.com/v1/images/generations"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-image-2-free",
    "prompt": "Cyberpunk hacker cracking a vault.",
    "n": 1,
    "size": "1024x1024",
    "response_format": "url"
}

res = requests.post(URL, headers=headers, json=data)
print(res.status_code)
print(res.text)
