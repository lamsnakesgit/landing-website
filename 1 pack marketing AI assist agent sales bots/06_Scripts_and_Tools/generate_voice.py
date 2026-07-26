import requests
import os

def get_api_key(name="OPENAI_API_KEY"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"{name}="):
                val = line.strip().split("=")[1].strip().strip("'\"")
                if val.endswith('.'): val = val[:-1]
                return val
    return os.environ.get(name)

api_key = get_api_key("AIHUBMIX_API_KEY")
if not api_key:
    api_key = get_api_key("OPENAI_API_KEY")

url = "https://api.aihubmix.com/v1/audio/speech" if get_api_key("AIHUBMIX_API_KEY") else "https://api.openai.com/v1/audio/speech"

text = "Первый — QWEN. Он генерирует и изображение, и видео. Да, он немного медленнее, но качество удивительно хорошее."
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
payload = {"model": "tts-1", "input": text, "voice": "nova", "response_format": "mp3"}

r = requests.post(url, json=payload, headers=headers)
if r.status_code == 200:
    with open("voice_2_new.mp3", "wb") as f:
        f.write(r.content)
    print("Успешно сгенерирован голос: voice_2_new.mp3")
else:
    print("Ошибка:", r.text)
