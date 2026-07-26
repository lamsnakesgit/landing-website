import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AIHUBMIX_API_KEY")

url = "https://api.aihubmix.com/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json()
        print("Image related models:")
        for model in models.get("data", []):
            name = model['id'].lower()
            if "image" in name or "dall" in name or "flux" in name or "midjourney" in name or "mj" in name:
                print(f"- {model['id']}")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print("Exception:", e)
