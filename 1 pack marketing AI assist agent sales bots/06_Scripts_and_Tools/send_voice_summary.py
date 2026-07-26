import os
import requests
import base64
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

TEXT = "Представьте, что вы больше не теряете ни одного клиента, а ваши стикеры сами продают за вас. Сегодня мы создали нечто потрясающее. Мы обошли жесткие лимиты корпоративного искусственного интеллекта от Гугл, настроили бессерверный шлюз, который будет ловить каждый лид абсолютно бесплатно. А еще, мы сгенерировали пак уникальных, кинематографичных ИИ-стикеров, которые бьют точно в боли B2B рынка. Это уже не просто автоворонка. Это ваша собственная армия ИИ-агентов, готовая работать на вас без перерывов и выходных. Вы готовы к запуску?"

VOICE = "ru-RU-DmitryNeural"
OUTPUT_FILE = "summary_voice.mp3"

async def generate_audio():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)

print("Generating voice message...")
asyncio.run(generate_audio())

EVO_URL = os.getenv("EVOLUTION_BASE_URL")
EVO_KEY = os.getenv("EVOLUTION_API_KEY")
EVO_INST = os.getenv("EVOLUTION_INSTANCE").strip()
PHONE = "77771269911"

with open(OUTPUT_FILE, "rb") as f:
    b64_audio = base64.b64encode(f.read()).decode("utf-8")

headers = {
    "apikey": EVO_KEY,
    "Content-Type": "application/json"
}

payload = {
    "number": PHONE,
    "audio": f"data:audio/mp3;base64,{b64_audio}",
    "delay": 1200,
    "encoding": True
}

url = f"{EVO_URL}/message/sendWhatsAppAudio/{EVO_INST}"

print(f"Sending audio to Evolution API ({url}) to number {PHONE}...")
res = requests.post(url, json=payload, headers=headers)
print(res.status_code, res.text)
