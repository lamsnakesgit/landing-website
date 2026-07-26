import asyncio
from pathlib import Path
import urllib.request
import urllib.parse
import uuid
import mimetypes
import edge_tts
import os
import json

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
        {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
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
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    
    doc_path = "all_skills_and_rules.md"
    
    print("Sending Document to Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendDocument",
        file_field="document",
        file_path=doc_path,
        caption="<b>🤖 Полный сборник правил и скиллов Клайна</b>\n(Все глобальные правила, хуки и custom skills)"
    )
    print(f"Doc Send Result: {status}, {ok}")

    voice_text = """
Готово! Я собрал абсолютно все наши локальные скиллы, глобальные правила и хуки клайна в один большой текстовый файл. Только что отправил его тебе документом, чтобы ты мог всё спокойно прочитать, так как текст слишком большой для одного сообщения.

Если вкратце пробежаться по твоему арсеналу:
Во-первых, у нас настроены строгие глобальные правила: фокус на выручку, прямые ссылки на настройки, запрет на удаление нод в эн-восемь-эн, регулярные коммиты и обязательное использование актуальной документации через веб-поиск.

Во-вторых, у нас мощнейшие правила продакшена видео: обязательное согласование раскадровки, паттерн карточек поверх спикера и автоматический рендер на удаленном сервере.

И в-третьих, у тебя настроен целый арсенал кастомных скиллов!
По маркетингу: парсеры лидов из Тредс и системы учета, ИИ-сейлз команда и рассылки в Ватсап.
По дизайну и видео: генерация каруселей, картинки Нано-Банана, Вео-видео, вырезание оговорок из аудио и сборка всего этого через ффмпег. 
Короче, у нас тут целая ИИ-студия под капотом. Открывай файлик, там расписан каждый скилл!
    """.strip()

    audio_path = "all_skills_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=voice_text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 all_skills_briefing.ogg >/dev/null 2>&1")
    
    print("Sending Voice via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="all_skills_briefing.ogg",
        caption="🎧 Голосовая выжимка всего арсенала скиллов"
    )
    print(f"Voice Send Result: {status}, {ok}")

if __name__ == "__main__":
    asyncio.run(main())
