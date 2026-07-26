import asyncio
from pathlib import Path
import urllib.request
import urllib.parse
import uuid
import mimetypes
import edge_tts
import os
import json

def send_telegram_text(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.status, '"ok":true' in resp.read().decode('utf-8', 'replace')

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
    tg_text = """
<b>🤖 Глобальные правила и скиллы агентов (Cline / Antigravity)</b>

1. <b>Общение:</b> Всегда на русском языке. Ответы прямые и четкие.
2. <b>Прямые ссылки (новое!):</b> Если нужно нажать что-то руками (настроить OAuth, выдать права) — агент ОБЯЗАН дать сначала прямую ссылку, и только потом инструкцию.
3. <b>Фокус на выручку:</b> Приоритет на действия, генерирующие прибыль (money making). Эффективные, устойчивые системы.
4. <b>n8n:</b> Строгий запрет на удаление нод без разрешения (можно только отключать связи). HTTP запросы даем в формате cURL.
5. <b>Кодинг:</b> Переменные на английском (camelCase/snake_case), комменты на русском. Современный ES2022+. Разбивка на мелкие чанки.
6. <b>Версионирование:</b> Обязательные Git коммиты каждые 5-10 минут во время работы.
7. <b>Авто-ресерч:</b> Если не хватает инфы (особенно по базам Supabase или нодам n8n) — агент сам лезет в Brave Search или Context7 MCP за свежей докой, а не выдумывает из головы.
    """.strip()
    
    bot_token = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g" # TG_REALSTATE_SMM_BOT
    chat_id = "888005446" # TG_CHAT_ID_MAIN
    
    print("Sending text to Telegram...")
    send_telegram_text(bot_token, chat_id, tg_text)

    voice_text = """
Привет! По твоей просьбе высылаю сводку глобальных правил и скиллов Клайна и других агентов.

Самое главное: фокус всегда на генерации выручки и прибыли. Мы строим устойчивые и эффективные системы, которые ведут к твоим финансовым целям.
Второе: если мне или другому агенту нужно, чтобы ты что-то сделал руками, например, залогинился или настроил доступ, мы теперь обязаны сначала дать тебе прямую ссылку на нужную страницу, и только потом писать пошаговую инструкцию. Больше никаких абстрактных "зайди в настройки".

По коду и разработке: общаемся и пишем комменты только на русском, а сами переменные — на английском. Код бьем на мелкие куски. 
По автоматизациям: в n8n мы никогда не удаляем ноды без твоего разрешения, можем только отключать связи, чтобы ничего не сломать. Если нам не хватает знаний по API или базам данных, мы не выдумываем, а сами автоматически идем в веб-поиск или читаем свежую документацию через наши внутренние инструменты. 
Ну и конечно, регулярные коммиты в гит каждые 5-10 минут!

Текстовую версию со списком я уже отправил сообщением выше. Двигаемся дальше!
    """.strip()

    audio_path = "global_skills_briefing.mp3"
    voice = "ru-RU-DmitryNeural"
    rate = "+0%"
    
    print("Generating TTS...")
    communicate = edge_tts.Communicate(text=voice_text, voice=voice, rate=rate)
    await communicate.save(audio_path)
    
    print("Converting to OGG Voice Note...")
    os.system(f"ffmpeg -y -i {audio_path} -vn -c:a libopus -b:a 32k -ar 48000 global_skills_briefing.ogg >/dev/null 2>&1")
    
    caption = "[VS Code Cline] \n🎧 Voice Briefing: Глобальные правила агентов"
    
    print("Sending voice via Telegram...")
    status, ok = send_telegram_file(
        bot_token=bot_token,
        chat_id=chat_id,
        method="sendVoice",
        file_field="voice",
        file_path="global_skills_briefing.ogg",
        caption=caption
    )
    print(f"Telegram API result: status={status}, ok={ok}")

if __name__ == "__main__":
    asyncio.run(main())
