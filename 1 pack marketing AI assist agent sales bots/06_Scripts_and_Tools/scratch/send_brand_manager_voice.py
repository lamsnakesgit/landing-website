import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import subprocess

def read_env(path=".env"):
    env = {}
    if not Path(path).exists():
        return env
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

async def make_mp3(text, audio_path, voice="ru-RU-DmitryNeural", rate="+2%"):
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
    body, boundary = multipart_form({"chat_id": chat_id, "caption": caption}, {file_field: file_path})
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/{method}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = resp.read().decode("utf-8", "replace")
            print(f"Status: {resp.status}, Response: {result}")
            return resp.status, '"ok":true' in result
    except urllib.error.HTTPError as e:
        error_message = e.read().decode('utf-8', 'replace')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response: {error_message}")
        return e.code, False
    except Exception as e:
        print(f"Error: {e}")
        return 500, False

async def main():
    env = read_env("../.env")
    bot_token = env.get("ANTIGRAVITY_BOT_TOKEN")
    chat_id = env.get("TG_CHAT_ID_MAIN")
    if not bot_token or not chat_id:
        print("Error: Missing Telegram credentials")
        return

    text = """Почему Meta не даёт верифицировать номер для бренда-менеджера? Обычно это происходит по трём причинам. Первая: номер уже используется в обычном Ватсапе или WhatsApp Business. Его нужно оттуда удалить. Вторая: это виртуальный номер или номер с плохой репутацией. Meta блокирует такие номера для API. Третья: баг с доставкой SMS. Попробуйте запросить звонок. 

Теперь по поводу статистики из Инстаграма. Да, это абсолютно реально. С помощью Instagram Graph API мы можем ежедневно или ежечасно вытягивать кучу данных: количество подписчиков, охваты, просмотры Reels, лайки, комментарии и репосты. 

Мы можем автоматизировать этот процесс через n8n. Система будет запрашивать данные через API Meta и передавать их нашему AI-агенту для анализа."""

    mp3_path = "brand_manager.mp3"
    ogg_path = "brand_manager.ogg"
    print("Generating MP3...")
    await make_mp3(text, mp3_path)
    print("Converting to OGG Opus...")
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", ogg_path], check=True)
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token, chat_id, 
        method="sendVoice", 
        file_field="voice", 
        file_path=ogg_path, 
        caption="[VS Code Cline]\n[Agent: Meta & n8n]\n🎧 Ответ про верификацию номера в Meta и выгрузку статистики (Reels, охваты, подписчики) для AI агента."
    )
    print(f"Sent Voice: {ok}")

if __name__ == "__main__":
    asyncio.run(main())
