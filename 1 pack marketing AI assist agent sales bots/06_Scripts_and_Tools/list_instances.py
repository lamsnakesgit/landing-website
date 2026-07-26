import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.env")

BASE_URL = os.getenv("EVOLUTION_BASE_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

url = f"{BASE_URL}/instance/fetchInstances"
response = requests.get(url, headers=headers)
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")
