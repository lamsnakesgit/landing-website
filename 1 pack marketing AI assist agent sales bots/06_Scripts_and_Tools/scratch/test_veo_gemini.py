import os
import sys
import json
import time
import subprocess
import requests

def log(msg):
    print(msg, flush=True)

# 1. Получаем токен доступа через наш Node.js скрипт
log("Getting OAuth2 Access Token from Node.js script...")
try:
    result = subprocess.run(["node", "scratch/get_google_token.js"], capture_output=True, text=True, check=True)
    access_token = result.stdout.strip()
    log(f"Token acquired. Length: {len(access_token)}")
except Exception as e:
    log(f"Failed to get token: {e}")
    if hasattr(e, "stderr") and e.stderr:
        log(f"Stderr: {e.stderr}")
    sys.exit(1)

# 2. Формируем запрос к Gemini Developer API для Veo 2.0
# Попробуем модели:
#  - veo-2.0-generate-001
#  - veo-3.0-generate-preview
#  - veo-3.1-generate-preview
model_id = "veo-2.0-generate-001"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predictLongRunning"

payload = {
    "instances": [
        {
            "prompt": "3D Pixar style animation. A giant, muscular man in a black leather jacket pointing finger aggressively, post-soviet courtyard, dramatic lighting."
        }
    ],
    "parameters": {
        "aspectRatio": "9:16",
        "durationSeconds": 5
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

log(f"Sending predictLongRunning request to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    log(f"Response Status: {response.status_code}")
    if response.status_code != 200:
        log(f"Error Response: {response.text}")
        # Попробуем резервную модель, если 2.0 недоступна
        if "not found" in response.text.lower() or "404" in response.text:
            log("Trying veo-3.0-generate-preview model instead...")
            url = "https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate-preview:predictLongRunning"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            log(f"Response Status for 3.0: {response.status_code}")
            log(f"Response: {response.text}")
        else:
            sys.exit(1)
    else:
        log(f"Success Response: {response.text}")
except Exception as e:
    log(f"Request failed: {e}")
    sys.exit(1)

# Парсим операцию
data = response.json()
op_name = data.get("name")
if not op_name:
    log("Error: No operation name in response.")
    sys.exit(1)

log(f"Operation started: {op_name}")

# 3. Поллинг состояния операции
poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}"
log(f"Polling URL: {poll_url}")

start_time = time.time()
while True:
    time.sleep(10)
    elapsed = int(time.time() - start_time)
    log(f"Checking operation status ({elapsed}s elapsed)...")
    try:
        res = requests.get(poll_url, headers=headers, timeout=15)
        if res.status_code == 200:
            op_data = res.json()
            done = op_data.get("done", False)
            if done:
                log("Operation completed!")
                log(json.dumps(op_data, indent=2))
                break
            else:
                metadata = op_data.get("metadata", {})
                progress = metadata.get("progressPercent", 0)
                log(f"Status: In Progress ({progress}%)")
        else:
            log(f"Error polling: {res.status_code} - {res.text}")
    except Exception as e:
        log(f"Polling request failed: {e}")
