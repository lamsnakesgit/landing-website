import requests
import os

api_key = "sk-fc9e63c2d08049c4a03b3f7b92977417"
url = "https://api.grsai.com/v1/images/generations"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "dall-e-3",
    "prompt": "Cyberpunk hacker in mafia suit, neon lights. Text reads: 'TEST'.",
    "n": 1,
    "size": "1024x1024"
}

response = requests.post(url, headers=headers, json=data)
print("GRSAI DALL-E 3 Response:", response.status_code)
print(response.text)
