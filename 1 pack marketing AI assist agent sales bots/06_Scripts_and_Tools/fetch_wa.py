import os
import requests
import json
from dotenv import load_dotenv
import urllib.parse

# Load env variables from the project directory
load_dotenv("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.env")

BASE_URL = os.getenv("EVOLUTION_BASE_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = os.getenv("EVOLUTION_INSTANCE")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

# The instance name might need URL encoding if it has a space
safe_instance = urllib.parse.quote(INSTANCE) if INSTANCE else "wa%201"

print(f"Connecting to instance: {safe_instance}")

# Get all contacts/chats
url = f"{BASE_URL}/chat/findChats/{safe_instance}"
try:
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        chats = response.json()
        print(f"Found {len(chats)} chats.")
        # Try to find the lawyer client
        found = False
        for chat in chats:
            name = chat.get('name', '')
            if name and ('Ма' in name or 'Юрист' in name or 'Ии' in name):
                print(f"Found match: {name} (ID: {chat.get('id')})")
                found = True
        if not found:
            print("Could not find the specific client by name. Here are the first 10 chats:")
            for chat in chats[:10]:
                print(f"Name: {chat.get('name')}, ID: {chat.get('id')}")
    else:
        print(f"Error fetching chats: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
