import asyncio
from pathlib import Path
import urllib.request
import uuid
import mimetypes
import edge_tts
import os

bot_token = os.environ.get("TG_REALSTATE_SMM_BOT", "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g")
chat_id = os.environ.get("TG_CHAT_ID_MAIN", "888005446")

text_ru = """
[VS Code Cline]
[Agent: N8N]
Привет! Это аудио-шпаргалка по тому, как тестировать твой новый воркфлоу и что значит "картинка с нодами".

Во-первых, картинка с нодами — это просто сам интерфейс n8n, где ты видишь блоки и стрелочки между ними. Когда мы используем n8n as code, мы пишем текстовый код, а программа сама выстраивает эти блоки и стрелочки на сервере, так что тебе не нужно перетаскивать их мышкой.

Во-вторых, как всё это тестировать. Зайди по ссылке в твой n8n. Внизу экрана ты увидишь кнопку Chat. Нажми её. Откроется интерфейс чата, как в обычном мессенджере. 
Напиши туда любой тестовый промпт, например: "Привет, сделай мне саммари", и отправь. 
Воркфлоу сразу запустится: сначала запрос пойдёт в бесплатный Groq. Если он зависнет, запрос пойдёт по красной ветке с ошибкой в Vertex AI. Если и он упадёт — запрос пойдёт в GRSAI.

По поводу GRSAI: я не могу вставить ключ сам через код, потому что n8n защищает пароли. Тебе нужно кликнуть два раза на ноду GRSAI LLM, нажать Select Credentials, затем Create New, и просто вставить туда твой ключ из файла точка env. То же самое нужно сделать для Groq и Vertex.
"""

async def make_mp3(text, audio_path, voice="ru-RU-SvetlanaNeural", rate="+5%"):
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
    audio_path = Path("n8n_test_guide.mp3")
    print("Generating audio...")
    await make_mp3(text_ru, audio_path)
    print("Sending to Telegram as voice note...")
    status, ok = send_telegram_file(
        bot_token, 
        chat_id, 
        "sendAudio", 
        "audio", 
        audio_path, 
        "[VS Code Cline] [Agent: N8N]\n🎧 Инструкция: Как тестировать n8n as code и настроить GRSAI."
    )
    print(f"sendAudio status={status} ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
