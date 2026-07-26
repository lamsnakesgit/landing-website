import asyncio
import urllib.request
import uuid
import mimetypes
from pathlib import Path
import os
import subprocess
import edge_tts

# Текст для озвучки
TEXT = """
Субагент вернулся и принес роскошный отчет! Я сохранил его для тебя в виде документа.

Вот самая мякотка, выжимка для CEO:

Первое. Балансировщики или Прокси-шлюзы: Никто в здравом уме не пишет костыли для смены ключей вручную. Весь Хай-Лоад сейчас сидит на опенсорсных LiteLLM или OneAPI. Они сами балансируют нагрузку, ротируют ключи, спасают при Rate Limits, падая на запасной ключ, и строят дашборды.

Второе. Как резать косты на 90 процентов: Нужно использовать Prompt Caching, то есть кэширование контекста. Ты один раз скармливаешь нейронке огромный системный промпт, например правила сейлза, она его кэширует, и все последующие запросы к этой базе стоят сущие копейки.

Третье. Бесплатный доступ к Топ моделям: Вместо обходов Terms of Service, стартапы просто забирают легальные программы. Тот же Google for Startups или GitHub Models дают бесплатный легальный доступ к GPT-4o и Claude 3.5 Sonnet просто по токену гитхаба.

Можешь изучить артефакт, там есть все ссылки на GitHub-репозитории!
"""

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"  # ANTIGRAVITY_BOT_TOKEN
CHAT_ID = "888005446"  # TG_CHAT_ID_MAIN

async def generate_audio():
    print("Генерируем MP3 через edge-tts...")
    communicate = edge_tts.Communicate(text=TEXT, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save("optimization.mp3")

def convert_to_ogg():
    print("Конвертируем MP3 в OGG (Opus) через ffmpeg для Telegram Voice Note...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "optimization.mp3",
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        "optimization_voice.ogg"
    ], check=True)

def multipart_form(fields, files):
    boundary = "----ClineBoundary" + uuid.uuid4().hex
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode())
        body.extend(b"\r\n")

    for name, path in files.items():
        path = Path(path)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode())
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary

def send_telegram_voice(file_path, caption):
    print("Отправляем sendVoice в Telegram...")
    body, boundary = multipart_form(
        {"chat_id": CHAT_ID, "caption": caption},
        {"voice": file_path},
    )

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = resp.read().decode("utf-8", "replace")
        print("Telegram API Response:", result)
        return resp.status, '"ok":true' in result

async def main():
    await generate_audio()
    convert_to_ogg()
    send_telegram_voice("optimization_voice.ogg", "[VS Code Antigravity]\n🎙️ Выжимка для CEO: Балансировщики, кэширование и фри-триалы.")

if __name__ == "__main__":
    asyncio.run(main())
