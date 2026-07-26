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
Привет! Разобрал твой лог с ошибкой "Unauthorized for this project" в n8n для Vertex LLM. 

Причина очень простая — несовпадение айди проекта!
В настройках ноды Vertex LLM ты вручную указал Project ID как `my-project-13652-10-7-25-7n`. 
Но я только что заглянул в твой локальный ключ vertex_sa.json, и там прописан совершенно другой проект! Правильный Project ID — это `my-project-28666-8-5-26-0-crm`. 

Чтобы всё починить: зайди в ноду Vertex LLM, сотри старый айдишник и вставь туда `my-project-28666-8-5-26-0-crm`. 

Если после этого всё равно будет ругаться, значит в самой консоли Google Cloud для этого проекта забыли включить Vertex AI API или привязать карту биллинга. Но на 99 процентов проблема именно в опечатке Project ID. Иди исправляй!
    """.strip()
    
    audio_path = "vertex_error_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 vertex_error_briefing.ogg >/dev/null 2>&1")
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Разбор ошибки Vertex AI в n8n"
    
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="vertex_error_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
