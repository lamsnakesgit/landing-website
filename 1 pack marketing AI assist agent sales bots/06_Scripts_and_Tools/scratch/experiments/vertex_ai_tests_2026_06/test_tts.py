import requests
import os

def get_api_key(name="OPENAI_API_KEY"):
    env_path = ".env"
    if not os.path.exists(env_path):
        env_path = "../.env"
    if not os.path.exists(env_path):
        env_path = "scripts/.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{name}="):
                    val = line.strip().split("=")[1].strip().strip("'\"")
                    if val.endswith('.'): val = val[:-1]
                    return val
    return os.environ.get(name)

api_key = get_api_key("AIHUBMIX_API_KEY") or get_api_key("OPENAI_API_KEY")
url = "https://api.aihubmix.com/v1/audio/speech" if get_api_key("AIHUBMIX_API_KEY") else "https://api.openai.com/v1/audio/speech"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

texts = [
    "Первый — Квен. Он генерирует и изображение, и видео. Да, он немного медленнее, но качество удивительно хорошее.",
    "Второй — Хуньюань. Он с открытым исходным кодом и позволяет создавать кинематографичные визуалы просто из запросов."
]

for i, t in enumerate(texts):
    payload = {"model": "tts-1", "input": t, "voice": "nova", "response_format": "mp3"}
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        with open(f"test_voice_{i+2}.mp3", "wb") as f:
            f.write(r.content)
        print(f"Успешно сгенерирован голос {i+2}, размер: {len(r.content)} байт")
    else:
        print("Ошибка:", r.text)
