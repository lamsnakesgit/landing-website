import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import os
import subprocess
import json

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

async def make_mp3(text, audio_path, voice="ru-RU-SvetlanaNeural", rate="+2%"):
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

def send_telegram_file(bot_token, chat_id, method, file_field, file_path, caption=""):
    fields = {"chat_id": chat_id}
    if caption:
        fields["caption"] = caption
        
    body, boundary = multipart_form(fields, {file_field: file_path})

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/{method}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = resp.read().decode("utf-8", "replace")
            print(f"{method} Result:", result)
            return resp.status, '"ok":true' in result
    except Exception as e:
        print(f"Error sending via {method}:", e)
        return 500, False

def send_telegram_message(bot_token, chat_id, text):
    data = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read().decode()
            print("sendMessage:", result)
    except Exception as e:
        print("sendMessage Error:", e)

async def main():
    env = read_env("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.env")
    
    # Try to find valid tokens
    bot_token = env.get("TG_REALSTATE_SMM_BOT") or env.get("TG_TARGET_BOT_TOKEN") or env.get("TG_SOURCE_BOT_TOKEN")
    chat_id = env.get("TG_CHAT_ID_MAIN") or env.get("TG_TARGET_CHAT_ID") or env.get("TG_SOURCE_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Could not find suitable Telegram tokens in .env")
        return
        
    print(f"Using bot: {bot_token[:10]}... chat_id: {chat_id}")

    script = """Привет! Это агент Antigravity. Пересказываю наш ликбез по архитектуре и памяти. Во-первых, почему бот тупит и забывает пароли? У агентов нет постоянной памяти между сессиями. Чтобы он всегда знал доступы, их нужно хранить в файле точка инви, а в глобальных правилах agents точка эмдэ прописать жесткое указание: доступы бери оттуда. Всё, больше он не спросит.
Во-вторых, разница между R A G и Обсидиан. Обсидиан — это просто папка с файлами и интерфейс, ваш источник знаний. А R A G — это механизм поиска. В n8n мы можем связать их: забирать тексты из Обсидиан, превращать в векторы и сохранять в базу данных Supabase. Затем бот сможет искать по ним ответы.
В-третьих, SaaS архитектура. Делать MVP на Supabase с Row Level Security — это лучшее решение для старта. R L S гарантирует, что чужие данные не пересекутся. Схема простая: Telegram бот получает сообщение, n8n ловит вебхук, проверяет юзера в Supabase и отдает ответ.
Дальше выбирайте: мы можем сейчас расписать SQL-схему для Supabase, либо собрать workflow в n8n."""

    base_dir = Path("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch")
    base_dir.mkdir(exist_ok=True)
    mp3_path = base_dir / "briefing.mp3"
    ogg_path = base_dir / "briefing.ogg"
    
    # Create MP3
    print("Generating MP3...")
    await make_mp3(script, mp3_path)
    
    # Convert to OGG using ffmpeg
    print("Converting to OGG...")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(mp3_path),
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        str(ogg_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Send Voice Note (OGG)
    print("Sending Voice Note...")
    send_telegram_file(
        bot_token, chat_id, "sendVoice", "voice", str(ogg_path), 
        caption="[VS Code Cline] 🎧 Голосовая шпаргалка: Архитектура, Память и MVP SaaS"
    )

    # Send MP3 
    print("Sending MP3 Audio...")
    send_telegram_file(
        bot_token, chat_id, "sendAudio", "audio", str(mp3_path),
        caption="[VS Code Cline] 🎙 Подкаст-версия ликбеза"
    )

    # Send Document
    md_path = Path("/Users/higherpower/.gemini/antigravity/brain/b644ff1b-aa71-49e2-a146-6a3b580050fc/agent_mastery_and_memory_guide.md")
    if md_path.exists():
        print("Sending Markdown Document...")
        send_telegram_file(
            bot_token, chat_id, "sendDocument", "document", str(md_path),
            caption="[VS Code Cline] 📄 Полный текстовый гайд (Markdown)"
        )
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
