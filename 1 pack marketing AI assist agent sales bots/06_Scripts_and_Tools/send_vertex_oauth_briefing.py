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
Понимаю, звучит как полная душнота от Гугла, но давай объясню проще.

Смотри, у нас есть две задачи: тексты и медиа. 

Первое — это тексты, то есть обычный Gemini. С ним всё супер просто. Забиваем на сложный Vertex, идём на сайт Google AI Studio, жмём там одну кнопку «Создать ключ», вставляем этот текст в n8n в зелёную ноду Gemini, и кайфуем. Деньги всё равно будут списываться с твоего триала на 300 баксов.

Второе — это картинки Нано Банана 2 и видео Вео. Они живут только в сложном Vertex AI. Раз Гугл запретил нам скачивать файлы-ключи, мы пойдём другим путём. Вспомни, как ты на разных сайтах авторизуешься через кнопку «Войти через Гугл». Вот в n8n мы сделаем точно так же! 

В Гугл Клауде ты создаешь так называемого OAuth-клиента — это буквально пара кликов. Он даст тебе два коротких кода: Client ID и Secret. Ты вставляешь их в n8n, нажимаешь там кнопку «Войти через Гугл», выбираешь свой аккаунт, и всё! Твой n8n получает полный доступ к Вео и картинкам без всяких файлов, админских ролей и прочей бюрократии. 

Короче: тексты делаем через AI Studio по простому ключу, а видео и картинки — через авторизацию «Войти через Гугл» в настройках Vertex AI. Ничего сложного, мы с этим быстро разберёмся!
    """.strip()
    
    audio_path = "vertex_oauth_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 vertex_oauth_briefing.ogg >/dev/null 2>&1")
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Как просто подключить Gemini, Veo и Imagen без файлов-ключей"
    
    print("Sending via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="vertex_oauth_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
