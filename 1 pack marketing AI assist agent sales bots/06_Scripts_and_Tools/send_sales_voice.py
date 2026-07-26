import os
import asyncio
import edge_tts
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("CONTENT_FACTORY_BOT").strip()
# Идентификатор пользователя из файла .env (TG_CHAT_ID_MAIN)
CHAT_ID = os.getenv("TG_CHAT_ID_MAIN").strip()

TEXT = """Привет! Давай разберем, как сделать автономных агентов, которые реально приносят деньги. Настоящее самообучение модели — это долго и дорого. В бизнесе мы делаем 'бизнес-самообучение' через динамическую базу данных и петлю обратной связи.
Для этого мы даем агенту инструмент записи в базу. И тут мы подходим к 'сохранению выигрышных паттернов' — тому самому winning patterns save.
Что это такое и как это работает? Представь, что агент генерирует десять разных офферов для строителей. Девять игнорируются, а один приносит созвон и продажу. 
В этот момент n8n или сам агент вызывает специальную функцию — save winning pattern. Она берет успешный текст оффера, фиксирует нишу, целевую аудиторию и чек, и сохраняет эту связку в базу данных, например, в Supabase.
В следующий раз, когда агенту нужно написать оффер для похожей ниши, он сначала вызывает инструмент 'поиск прошлых успехов'. Он читает базу, видит, что сработало в прошлый раз, и берет этот текст за основу, а не придумывает с нуля. 
То есть, бот буквально накапливает опыт успешных продаж. Чем больше он пишет и продает, тем умнее и точнее становятся его следующие сообщения.
Добавляем сюда полную автономию: ставим n8n на крон, он парсит лидов из 2GIS, передает агенту, агент смотрит в базу успешных паттернов, пишет точечные офферы и рассылает их в WhatsApp. Если кто-то отвечает — подключается сейлз-бот, обученный на Хормози и Дашкиеве, закрывает возражения и доводит до зума. Вот так это работает!"""

VOICE = "ru-RU-DmitryNeural"
MP3_FILE = "sales_agent_explanation.mp3"
OGG_FILE = "sales_agent_explanation.ogg"

async def generate_audio():
    print("Generating MP3 with edge-tts...")
    communicate = edge_tts.Communicate(TEXT, VOICE, rate="+5%")
    await communicate.save(MP3_FILE)

def convert_to_ogg():
    print("Converting MP3 to OGG Opus...")
    # ffmpeg -y -i input.mp3 -vn -c:a libopus -b:a 32k -ar 48000 output.ogg
    subprocess.run(["ffmpeg", "-y", "-i", MP3_FILE, "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", OGG_FILE], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def send_voice():
    print("Sending OGG voice to Telegram...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
    with open(OGG_FILE, "rb") as f:
        res = requests.post(url, data={"chat_id": CHAT_ID}, files={"voice": f})
    print("Telegram Response:", res.json())

if __name__ == "__main__":
    asyncio.run(generate_audio())
    try:
        convert_to_ogg()
        send_voice()
    except Exception as e:
        print("Error during conversion/sending:", e)
        print("Falling back to sending MP3 as audio file...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        with open(MP3_FILE, "rb") as f:
            res = requests.post(url, data={"chat_id": CHAT_ID}, files={"audio": f})
        print("Fallback Telegram Response:", res.json())
