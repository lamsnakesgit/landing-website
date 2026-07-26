import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import os

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
        {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
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
    text = """
Привет! Посмотрел твои скрины из админки Гугла. Ты пытаешься выдать себе роль Администратора политик, но выбираешь Recommender Admin. 

Но если честно, давай вообще забьем на эти сервисные аккаунты, потому что у Гугла сейчас паранойя, и они намертво блочат ключи для новых аккаунтов.

Слушай лучший и самый быстрый способ: мы подключим тот же самый Gemini, с тем же самым твоим фри-триалом, но через Google AI Studio. 

Зайди на сайт aistudio.google.com/app/apikey. Нажми там синюю кнопку Create API Key и выбери твой проект из выпадающего списка. Гугл сгенерирует тебе текстовый ключ. 

Потом идешь в n8n, удаляешь тугую ноду Vertex LLM, и вместо нее ставишь ноду Google Gemini Chat Model. Создаешь в ней креды, вставляешь этот ключ, и всё! Никаких танцев с бубном вокруг политик безопасности, а биллинг так же будет идти с твоего триала.
    """.strip()
    
    audio_path = "aistudio_bypass_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 aistudio_bypass_briefing.ogg >/dev/null 2>&1")
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Обход блокировок через Google AI Studio"
    
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="aistudio_bypass_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
