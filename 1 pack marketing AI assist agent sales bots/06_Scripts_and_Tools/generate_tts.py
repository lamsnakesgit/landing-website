import os
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aihubmix.com/v1" # Assuming AIHubMix OpenAI proxy
)

script_parts = [
    "90% экспертов сливают бюджет на Reels, потому что делают эту ошибку...",
    "Они тратят часы на съемку, забывая про удержание внимания в первые секунды.",
    "Сохраняй это видео, сейчас покажу, как автоматизировать монтаж и собирать миллионы просмотров!"
]

for i, text in enumerate(script_parts):
    print(f"Генерация аудио {i+1}...")
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text
        )
        response.stream_to_file(f"clip_{i+1}.mp3")
        print(f"clip_{i+1}.mp3 сохранен!")
    except Exception as e:
        print(f"Ошибка: {e}")
