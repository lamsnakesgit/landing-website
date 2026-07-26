import asyncio
import urllib.request
import uuid
import mimetypes
from pathlib import Path
import os
import subprocess
import edge_tts

TEXT = """
Субагент Архитектор успешно запущен!
Он ушел в фоновый режим и сейчас шерстит интернет, чтобы создать подробный бизнес-артефакт. 
Он пропишет схему "Офиса ИИ-сотрудников", расставит роли: кто лидоруб, кто маркетолог, кто сейлз. 
Продумает архитектуру SaaS — как мы всё это упакуем в продукт. 
И самое главное — распишет модель монетизации: как мы будем продавать доступ к этим агентам другим бизнесам по API или по подписке. 

Как только он закончит свой анализ, я сделаю выжимку и запишу тебе еще одно голосовое с готовым результатом и бизнес-планом! А пока мы можем продолжать писать код для нашего бота.
"""

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

async def generate_audio():
    print("Генерируем MP3 через edge-tts...")
    communicate = edge_tts.Communicate(text=TEXT, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save("architect_launch.mp3")

def convert_to_ogg():
    print("Конвертируем MP3 в OGG (Opus)...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "architect_launch.mp3",
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        "architect_launch.ogg"
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
    send_telegram_voice("architect_launch.ogg", "🚀 Субагент-Архитектор: Запуск анализа SaaS и монетизации")

if __name__ == "__main__":
    asyncio.run(main())
