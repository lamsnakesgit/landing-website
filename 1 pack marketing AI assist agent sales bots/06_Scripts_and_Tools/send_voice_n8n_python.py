import asyncio
import urllib.request
import uuid
import mimetypes
from pathlib import Path
import os
import subprocess
import edge_tts

TEXT = """
Спокойно, без паники! Давай разберем, как нам получить крутых агентов в телефоне через Телеграм, чтобы это работало как часы и не стоило как крыло самолета.

Проблема с Гугл Антигравити SDK в том, что это внутренний фреймворк редактора. Он идеален для написания кода здесь, за компом, но не подходит для деплоя на внешний сервер для связи с Телеграмом.

Но нам и не нужен этот SDK, чтобы собрать мощного агента! Агент — это просто логика: получил текст, подумал, дернул инструмент, ответил. У нас есть три роскошных пути, как сделать это бесплатно или за копейки:

Первый путь: n8n. Визуальные агенты — идеальный вариант. Ты ставишь n8n на свой сервер бесплатно. Там есть встроенные узлы AI Agent. Триггером будет сообщение в Telegram. Мозгом — твой бесплатный ключ AIHubMix или GrsAI. А руками — доступы к базам данных и парсерам. Итог: общаешься с агентом с телефона, он думает через бесплатные токены. Ноль кода, работает 24 на 7.

Второй путь: Open-Source Python Фреймворки. Если хочешь именно кодом, берем открытые фреймворки, например smolagents от HuggingFace или Pydantic-AI. Пишем скрипт, подключаем ключ, прикручиваем Телеграм-бота, и он сможет гуглить и читать файлы, а платить ты будешь только за дешевые токены.

Третий путь: Наш текущий бот. Бот, которого мы сейчас запустили — это уже ассистент. Мы можем просто научить его дергать инструменты напрямую через API, добавив логику Function Calling.

Что решаем? Если нужны сложные бизнес-процессы, рассылки, парсинг — давай перенесем сборку бота в n8n. Это сэкономит кучу нервов. Если хочешь кодом — перепишем бота на открытый питон фреймворк. Что выберем?
"""

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"  # ANTIGRAVITY_BOT_TOKEN
CHAT_ID = "888005446"  # TG_CHAT_ID_MAIN

async def generate_audio():
    print("Генерируем MP3 через edge-tts...")
    communicate = edge_tts.Communicate(text=TEXT, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save("n8n_python.mp3")

def convert_to_ogg():
    print("Конвертируем MP3 в OGG (Opus) через ffmpeg для Telegram Voice Note...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "n8n_python.mp3",
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        "n8n_python_voice.ogg"
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
    send_telegram_voice("n8n_python_voice.ogg", "[VS Code Antigravity]\n🎙️ Архитектура агентов в Telegram: n8n vs Python-фреймворки")

if __name__ == "__main__":
    asyncio.run(main())
