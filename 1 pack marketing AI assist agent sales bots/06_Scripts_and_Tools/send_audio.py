import asyncio
import os
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import subprocess

bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
chat_id = "888005446"

text = """Привет! Давай быстро разберем разницу между Antigravity и Antigravity IDE. 
Antigravity — это сам движок и фреймворк. Он идеален для долгих фоновых задач, когда нужно собрать архитектуру, сделать масштабный рефакторинг или оркестрировать много агентов одновременно. Но он работает через терминал и не видит твой курсор в редакторе. 
А вот Antigravity IDE — это плагин для твоего редактора кода. Он видит твои открытые файлы, позицию курсора и ошибки линтера. Это идеальный вариант для парного программирования, быстрых правок кода и дебага. Изменения ты видишь сразу в виде удобного дифа. 
Итог такой: хочешь писать код здесь и сейчас — бери IDE. Нужна автономная машина для сложных фоновых задач — используй базовый Antigravity. Надеюсь, стало понятнее!"""

audio_path = Path("briefing.mp3")
voice_path = Path("briefing.ogg")

async def make_mp3(text, path, voice="ru-RU-SvetlanaNeural", rate="+2%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(path))

def convert_to_ogg(input_mp3, output_ogg):
    subprocess.run([
        "ffmpeg", "-y", "-i", str(input_mp3),
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        str(output_ogg)
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

def send_telegram_file(bot_token, chat_id, method, file_field, file_path, caption):
    body, boundary = multipart_form(
        {"chat_id": chat_id, "caption": caption},
        {file_field: file_path},
    )

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/{method}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=90) as resp:
        result = resp.read().decode("utf-8", "replace")
        return resp.status, '"ok":true' in result

async def main():
    print("Генерация MP3...")
    await make_mp3(text, audio_path)
    
    print("Конвертация в OGG...")
    convert_to_ogg(audio_path, voice_path)
    
    print("Отправка голосового сообщения...")
    status, ok = send_telegram_file(
        bot_token, chat_id, "sendVoice", "voice", voice_path, "[VS Code Cline] Аудио-шпаргалка: Antigravity vs Antigravity IDE"
    )
    
    print(f"Отправка sendVoice: HTTP {status}, ok={ok}")
    
    # Clean up
    if audio_path.exists():
        audio_path.unlink()
    if voice_path.exists():
        voice_path.unlink()

if __name__ == "__main__":
    asyncio.run(main())
