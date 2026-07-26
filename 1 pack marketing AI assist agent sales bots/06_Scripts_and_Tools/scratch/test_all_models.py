import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AIHUBMIX_API_KEY")

models = [
    "gpt-image-2",
    "gpt-image-2-free",
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
    "dall-e-3",
    "dall-e-2"
]

url = "https://api.aihubmix.com/v1/images/generations"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

for model in models:
    print(f"\n--- Trying model: {model} ---")
    payload = {
        "model": model,
        "prompt": "A young woman wearing a white bathrobe, towel wrapped around her hair, smiling, photorealistic",
        "n": 1,
        "size": "1024x1024" if "dall-e" in model or "gpt" in model else "1024x1024"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS!")
            print(response.json())
            break
        else:
            print(response.text[:200])
    except Exception as e:
        print("Exception:", e)
