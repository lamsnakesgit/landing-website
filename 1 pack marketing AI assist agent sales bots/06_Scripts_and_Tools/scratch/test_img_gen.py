import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AIHUBMIX_API_KEY")

# Test 1: Chat completions
print("--- TEST 1: /v1/chat/completions ---")
url_chat = "https://api.aihubmix.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload_chat = {
    "model": "gpt-image-2",
    "messages": [
        {"role": "user", "content": "Generate a photorealistic portrait of a young woman with a towel wrapped around her hair, wearing a white bathrobe, smiling, high quality"}
    ]
}

try:
    response = requests.post(url_chat, json=payload_chat, headers=headers)
    print("Chat completions response status:", response.status_code)
    print("Chat completions response text:", response.text[:1000])
except Exception as e:
    print("Chat completions exception:", e)

# Test 2: Images generations
print("\n--- TEST 2: /v1/images/generations ---")
url_img = "https://api.aihubmix.com/v1/images/generations"
payload_img = {
    "model": "gpt-image-2",
    "prompt": "Generate a photorealistic portrait of a young woman with a towel wrapped around her hair, wearing a white bathrobe, smiling, high quality",
    "n": 1,
    "size": "1024x1024"
}

try:
    response = requests.post(url_img, json=payload_img, headers=headers)
    print("Images generations response status:", response.status_code)
    print("Images generations response text:", response.text[:1000])
except Exception as e:
    print("Images generations exception:", e)
