import os
import sys
import json
import time
import requests

# Промпт для Сцены 1: Аха и Бейк в постсоветском дворе
SCENE_1_PROMPT = (
    "3D Pixar-style animation, cinematic. A giant intimidating man 'Bake' in a black leather jacket "
    "stands in a post-Soviet courtyard at night, dramatic neon lighting. He points his finger "
    "aggressively at a slim clever-looking AI robot 'Axa'. The robot looks calm and analytical. "
    "Camera slowly zooms in. Photorealistic textures, dark atmosphere, 8-10 seconds."
)

API_KEY = "AIzaSyD5jmzR6scSp-KsRH0ECOjSqLbemAfQWw0"
MODEL = "veo-2.0-generate-001"

def log(msg):
    print(msg, flush=True)

# Пробуем predictLongRunning через Developer API с API Key
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:predictLongRunning?key={API_KEY}"

payload = {
    "instances": [
        {
            "prompt": SCENE_1_PROMPT
        }
    ],
    "parameters": {
        "aspectRatio": "9:16",
        "durationSeconds": 8,
        "sampleCount": 1
    }
}

log(f"Отправляем запрос Veo 2.0...")
log(f"URL: {url[:80]}...")

try:
    response = requests.post(url, json=payload, timeout=30)
    log(f"Статус: {response.status_code}")
    log(f"Ответ: {response.text[:500]}")
except Exception as e:
    log(f"Ошибка запроса: {e}")
    sys.exit(1)

if response.status_code != 200:
    # Пробуем альтернативный endpoint — generateContent стиль
    log("\nПробуем альтернативный endpoint...")
    url2 = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    payload2 = {
        "contents": [
            {
                "parts": [
                    {"text": SCENE_1_PROMPT}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["VIDEO"],
            "videoConfig": {
                "aspectRatio": "9:16",
                "durationSeconds": 8
            }
        }
    }
    r2 = requests.post(url2, json=payload2, timeout=30)
    log(f"Статус альт: {r2.status_code}")
    log(f"Ответ альт: {r2.text[:1000]}")
    sys.exit(0)

# Успех — парсим операцию
data = response.json()
op_name = data.get("name")
if not op_name:
    log(f"Нет operation name. Полный ответ: {json.dumps(data, indent=2)}")
    sys.exit(1)

log(f"Операция запущена: {op_name}")

# Поллинг
poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={API_KEY}"
log(f"Ждём результата...")

for attempt in range(30):
    time.sleep(15)
    elapsed = (attempt + 1) * 15
    log(f"Проверяем ({elapsed}s)...")
    try:
        res = requests.get(poll_url, timeout=15)
        if res.status_code == 200:
            op_data = res.json()
            if op_data.get("done"):
                log("✅ Готово!")
                log(json.dumps(op_data, indent=2))
                # Сохраняем результат
                with open("scratch/veo_result.json", "w") as f:
                    json.dump(op_data, f, indent=2)
                log("Сохранено в scratch/veo_result.json")
                break
            else:
                progress = op_data.get("metadata", {}).get("progressPercent", "?")
                log(f"В процессе... {progress}%")
        else:
            log(f"Ошибка поллинга: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        log(f"Ошибка: {e}")
