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
Как работает математика токенов, или почему Субагенты в разы дешевле.

Смотри, ты платишь не за сам факт вызова нейросети, а за объем переданного текста, то есть контекста, в каждом запросе. 
Если я, твой Главный Агент, буду сам делать 100 запросов в Google для ресерча, то с каждым новым шагом я буду отправлять серверу всю нашу с тобой историю переписки, которая уже весит десятки тысяч токенов! Это называется "раздувание контекста". К сотому шагу поиска каждый мой чих будет стоить по 10 центов.

Но когда я вызываю Субагента — я создаю абсолютно чистого клона. У него в памяти ровно ноль слов. Я даю ему один короткий промпт: "Ищи вот это". Он делает свои 100 запросов с пустым легким контекстом, что стоит тысячные доли цента, а потом просто приносит мне готовую выжимку-результат. 

Итог: мы экономим 90 процентов денег на токенах, не теряя при этом качество работы.
"""

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"  # ANTIGRAVITY_BOT_TOKEN
CHAT_ID = "888005446"  # TG_CHAT_ID_MAIN

async def generate_audio():
    print("Генерируем MP3 через edge-tts...")
    communicate = edge_tts.Communicate(text=TEXT, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save("tokens.mp3")

def convert_to_ogg():
    print("Конвертируем MP3 в OGG (Opus) через ffmpeg для Telegram Voice Note...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "tokens.mp3",
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        "tokens_voice.ogg"
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
    send_telegram_voice("tokens_voice.ogg", "[VS Code Antigravity]\n🎙️ Математика токенов: Почему субагенты экономят 90% бюджета.")

if __name__ == "__main__":
    asyncio.run(main())
