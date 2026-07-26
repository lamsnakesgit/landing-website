import asyncio
import urllib.request
import uuid
import mimetypes
from pathlib import Path
import os
import subprocess
import edge_tts

# Текст для озвучки (Markdown символы убраны для чистого чтения)
TEXT = """
Это самый важный вопрос, который ты задал за всё время. Потому что попытка запустить пять разных агентов без единой структуры — это гарантия сто процентного хаоса, перезатертых файлов и потерянных денег.

Но построить реальный "Офис ИИ-сотрудников 24 на 7", который разрабатывает Саас сервисы, ведет блог и генерит продажи на высокий чек — абсолютно реально. Это называется AI-Automated Agency, или сокращенно AAA.

Чтобы это приносило деньги, а не головную боль, нужно внедрить строгий регламент, так называемый Анти-Хаос фреймворк. Вот как мы это сделаем:

Правило первое: Единый источник правды (Код и Файлы).
У тебя есть Мак, есть VPS и куча нетрекаемых файлов. Это первая точка хаоса. Решение: Гитхаб становится "офисом". Ни один агент не работает просто в папке. Твои агенты в VS Code на Маке пишут код Саас-проекта и коммитят это в Гитхаб. На VPS, где живет твой Telegram-бот, настроен авто-pull. Как только код обновился на Гитхабе, VPS сам его скачивает и перезапускает. Никаких конфликтов: если ты хочешь, чтобы бот в Телеграме сам написал код, он должен создавать новую ветку в Git, а не ломать основной код.

Правило второе: Строгое разделение ролей.
Не заставляй всех агентов делать всё подряд. Раздели их как реальных людей:
Первое. VS Code на Маке — это твой IT-отдел. Ты их включаешь только когда нужно написать новый код или сделать лендинг.
Второе. Telegram-бот на VPS — это твой Операционный Директор и Личный Помощник. Работает 24 на 7. Он не пишет ядро проектов, он управляет продажами, дергает лидорубов, шлет отчеты и общается с тобой.
Третье. N 8 N — это твой отдел интеграций, или "Сантехники". Они связывают вебхуки, Google Sheets, Trello и Telegram.

Правило третье: Единая шина данных для денег и метрик.
Чтобы трекать спенды на АПИ, движение денежных средств и РОИ, тебе нужна одна база данных. Например, Supabase или Airtable. Каждый субагент в конце своей работы обязан записать метрику. В конце дня твой Telegram-бот собирает эту табличку и пишет тебе отчет: "Босс, потрачено 2 доллара, найдено 45 лидов, отправлено 12 офферов".

Правило четвертое: Изолированные "Песочницы".
Если ты делаешь клиентские проекты на высокий чек, каждый клиент должен лежать в отдельном репозитории и Докер-контейнере. Иначе один сбой сольет данные клиента А клиенту Б.

Резюме: С чего начать разгребать этот хаос прямо сейчас?
Нам нужно сделать первый физический шаг: Зайти в твою папку на Маке, сделать git init, написать gitignore и залить это всё в приватный репозиторий Гитхаб. Затем зайти на VPS, склонировать репозиторий и настроить CI CD. Как только мы это сделаем — хаос исчезнет. Твои агенты будут работать синхронно. Начинаем превращать эту папку в структурированный Гитхаб-репозиторий?
"""

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"  # ANTIGRAVITY_BOT_TOKEN
CHAT_ID = "888005446"  # TG_CHAT_ID_MAIN

async def generate_audio():
    print("Генерируем MP3 через edge-tts...")
    communicate = edge_tts.Communicate(text=TEXT, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save("framework.mp3")

def convert_to_ogg():
    print("Конвертируем MP3 в OGG (Opus) через ffmpeg для Telegram Voice Note...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "framework.mp3",
        "-vn", "-c:a", "libopus", "-b:a", "32k", "-ar", "48000",
        "framework_voice.ogg"
    ], check=True)

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

def send_telegram_voice(file_path, caption):
    print("Отправляем sendVoice в Telegram...")
    body, boundary = multipart_form(
        {"chat_id": CHAT_ID, "caption": caption},
        {"voice": file_path},
    )

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = resp.read().decode("utf-8", "replace")
        print("Telegram API Response:", result)
        return resp.status, '"ok":true' in result

async def main():
    await generate_audio()
    convert_to_ogg()
    send_telegram_voice("framework_voice.ogg", "[VS Code Antigravity]\n🎙️ Анти-Хаос фреймворк и структура AI-Агентства (AAA).")

if __name__ == "__main__":
    asyncio.run(main())
