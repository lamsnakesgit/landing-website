import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import os
import subprocess

def read_env(path=".env"):
    env = {}
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

async def make_mp3(text, audio_path, voice="ru-RU-DmitryNeural", rate="+5%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(audio_path))

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
    env = read_env()
    bot_token = env.get("TG_REALSTATE_SMM_BOT")
    chat_id = env.get("TG_CHAT_ID_MAIN") or env.get("TG_REALSTATE_SMM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Missing bot token or chat ID")
        return

    text = """Привет! Разбираем твой план. Под Сиданс 3 ты скорее всего имеешь в виду Runway Gen-3 Alpha, а Сиданс 2 — это старая Gen-2. Голосовой ввод часто так коверкает слово Джен. Джен 3 на голову выше. Она понимает сложные промпты, делает гиперреализм и генерит видео до 10 секунд. Джен 2 дешевле, но качество там мыльное и сильно плывет. Так что если качество важно — бери только Джен 3.

Во-вторых, твоя идея юзать Google Veo API на бесплатном триале — это супер мощный ход! Модель Veo шикарно делает говорящие головы и сложные сцены.

В-третьих, автоматизировать создание сериалов и мультиков через API. Это именно то, что делает Fable Studio! Мы можем настроить связку: Claude 3.5 Sonnet или GPT-4o пишет сценарий и промпты, дальше Veo генерит сцены, Эдж-ти-ти-эс делает озвучку, а скрипт на FFmpeg всё это монтирует. Это топовый пайплайн для создания вирусного контента. Скажи, если хочешь, чтобы я собрал такую автоматизацию!"""

    mp3_path = "reply.mp3"
    ogg_path = "reply.ogg"
    
    print("Generating MP3...")
    await make_mp3(text, mp3_path)
    
    print("Converting to OGG...")
    subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path, "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", ogg_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Sending to Telegram...")
    caption = "[VS Code Cline]\n[Agent: AntiGravity]\n🎙️ Ответ про Runway Gen-3, Google Veo и AI-сериалы"
    status, ok = send_telegram_file(bot_token, chat_id, "sendVoice", "voice", ogg_path, caption)
    print(f"Sent Voice: status={status} ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
