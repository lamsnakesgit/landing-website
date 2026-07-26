import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("EVOLUTION_BASE_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = os.getenv("EVOLUTION_INSTANCE").strip() # Ensure no trailing spaces

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

print(f"Fetching groups for instance: {INSTANCE} from {BASE_URL}")
url = f"{BASE_URL}/group/fetchAllGroups/{INSTANCE}"
try:
    response = requests.get(url, headers=headers, params={"getParticipants": "true"})
    if response.status_code == 200:
        groups = response.json()
        print(f"Found {len(groups)} groups.")
        for g in groups[:5]:
            print(f"- {g.get('subject', 'Unknown')} ({g.get('id')}) | Participants: {len(g.get('participants', []))}")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
