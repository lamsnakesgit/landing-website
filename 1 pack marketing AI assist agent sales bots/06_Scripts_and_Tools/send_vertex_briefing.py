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
Привет! Это Клайн. Отвечаю на твой вопрос про Vertex API и обход лимитов Gemini. 

Чтобы агенты списывали токены с триального баланса Google Cloud на июнь двадцать шестого года, а не упирались в стандартные лимиты бесплатного API-ключа, нам нужно перевести их на авторизацию через Service Account. 

В корне твоего проекта уже лежит файл vertex_sa.json. Это и есть сервисный аккаунт, привязанный к проекту с биллингом. 
Всё, что нужно сделать — это прописать в переменных окружения агента строчку: GOOGLE_APPLICATION_CREDENTIALS равно путь к этому файлу. 

После этого, когда агент вызывает модель Gemini, он должен обращаться не к стандартному google-api, а указывать провайдера vertex_ai. Например, vertex_ai/gemini-1.5-pro. 

Таким образом, все запросы агента пойдут напрямую в Google Cloud, биллинг будет капать на твой триальный аккаунт, а жесткие лимиты на количество запросов в минуту отвалятся. Всё просто!
    """.strip()
    
    audio_path = "vertex_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 vertex_briefing.ogg >/dev/null 2>&1")
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Vertex AI Gemini & Free Trial 2026"
    
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="vertex_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
