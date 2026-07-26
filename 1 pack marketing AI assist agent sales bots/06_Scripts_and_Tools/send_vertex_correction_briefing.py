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
Ааа, понял! Посмотрел в папку Загрузки и нашел твой новый файлик для проекта 13-652 с фри-триалом!

Смотри, в чём дело: Project ID в ноде ты указал правильно — от нового проекта. 
НО! Сама учетка, которую ты выбрал в поле Credential в n8n (которая называется account 2 вы7т), содержит приватный ключ от СТАРОГО проекта! 

Поэтому n8n берёт ключ от старого проекта и пытается достучаться до нового, и Гугл посылает его подальше.

Что надо сделать:
Иди в n8n, открой настройки Credentials (доступы). Найди там этот Google Service Account. Открой у себя на компе в блокноте этот новый скачанный джейсон-файл, скопируй весь текст и вставь его туда в n8n вместо старого! Либо просто создай новую Credential и выбери её в ноде. 

И всё! Твой агент поедет на новеньком триале. А я, кстати, уже подтянул этот новый файлик в корень нашего проекта, так что мои внутренние питоновские скрипты тоже будут юзать свежий фри триал. Починяй креды в n8n и погнали делать карусели!
    """.strip()
    
    audio_path = "vertex_correction_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 vertex_correction_briefing.ogg >/dev/null 2>&1")
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Уточнение по новому ключу Vertex"
    
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="vertex_correction_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
