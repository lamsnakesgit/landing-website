import requests
import time
import sys

API_KEY = "B6D711FCDE4D4FD5936544120E713976"
BASE_URL = "http://127.0.0.1:8080"
headers = {"apikey": API_KEY, "Content-Type": "application/json"}
number = "77771269911"

print("Deleting instance number1...")
requests.delete(f"{BASE_URL}/instance/delete/number1", headers=headers)
time.sleep(2)

print("Creating instance number1...")
res = requests.post(
    f"{BASE_URL}/instance/create",
    json={"instanceName": "number1", "integration": "WHATSAPP-BAILEYS", "generateToken": False},
    headers=headers
)
print("Create response:", res.status_code, res.text)
time.sleep(2)

print("Fetching pairing code...")
res = requests.get(
    f"{BASE_URL}/instance/connect/number1?number={number}",
    headers=headers
)
print("Connect response:", res.status_code)
data = res.json()
if "pairingCode" in data:
    print(f"PAIRING_CODE_FOUND: {data['pairingCode']}")
else:
    print("NO_PAIRING_CODE", list(data.keys()))
