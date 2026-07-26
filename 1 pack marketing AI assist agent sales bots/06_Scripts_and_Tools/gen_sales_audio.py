import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

TEXT = """Слушай, обычную рекламу сейчас все пролистывают на автомате — у людей жуткая баннерная слепота. Но знаешь, что никто и никогда не игнорит? Крутые, жизненные стикеры в рабочих чатах. 

Фишка в том, что мы делаем для бизнеса кастомные стикерпаки — с твоим лицом, логотипом или маскотом, и главное — с твоим водяным знаком. Это гениальный маркетинг, потому что ты платишь за создание ровно один раз, а дальше он работает на тебя бесконечно. 

Ты просто кидаешь их в чаты во время переписок. Людям нравится, они сохраняют стикер себе и начинают отправлять его своим клиентам и друзьям. Получается вирусная петля: твой бренд и твой никнейм бесплатно разлетаются по всему Телеграму и Вотсапу руками других людей. Нативная, бесплатная реклама, которая не бесит.

Если хочешь внедрить такой партизанский маркетинг себе в бизнес и получить стикерпак, который будет качать тебе трафик 24/7 — пиши в личку, придумаем огненную концепцию именно под твою нишу."""

async def make_mp3(text, audio_path, voice="ru-RU-DmitryNeural", rate="+0%"):
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

def send_telegram_file(method, file_field, file_path, caption=""):
    body, boundary = multipart_form(
        {"chat_id": CHAT_ID, "caption": caption},
        {file_field: file_path},
    )
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = resp.read().decode("utf-8", "replace")
        return resp.status, '"ok":true' in result

async def main():
    mp3_path = "sales_pitch.mp3"
    ogg_path = "sales_pitch.ogg"
    
    print("Generating MP3...")
    await make_mp3(TEXT, mp3_path)
    
    print("Converting to OGG...")
    subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path, "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", ogg_path
    ], check=True)
    
    print("Sending Audio (MP3)...")
    send_telegram_file("sendAudio", "audio", mp3_path, "🎙 Продающее аудио (MP3 формат)")
    
    print("Sending Voice (OGG)...")
    send_telegram_file("sendVoice", "voice", ogg_path, "")
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
