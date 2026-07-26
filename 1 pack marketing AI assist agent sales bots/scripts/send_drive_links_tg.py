#!/usr/bin/env python3
"""Отправка ссылок на Google Drive файлы в Telegram"""

import urllib.request
import urllib.parse
import json
from pathlib import Path

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

BASE_DIR = Path(__file__).parent.parent
RESULTS_FILE = BASE_DIR / "drive_upload_results.json"

def send_message(text):
    data = urllib.parse.urlencode({
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': 'false'
    }).encode('utf-8')

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return None


def main():
    if not RESULTS_FILE.exists():
        print("❌ Файл результатов не найден")
        return

    with open(RESULTS_FILE) as f:
        data = json.load(f)

    folder_link = data.get("folder_link", "")
    files = data.get("files", [])

    # Формируем сообщение
    lines = [
        "📁 *Файлы проекта ИИ Юрист загружены на Google Drive*",
        "",
        f"📂 [Открыть папку]({folder_link})",
        "",
        "*Файлы:*",
    ]

    for i, file in enumerate(files, 1):
        name = file.get("name", "Без имени")
        link = file.get("link", "")
        lines.append(f"{i}. [{name}]({link})")

    lines.append("")
    lines.append("✅ Все файлы открыты для доступа по ссылке")

    text = "\n".join(lines)

    result = send_message(text)
    if result and result.get("ok"):
        print("✅ Сообщение отправлено в Telegram")
    else:
        print(f"❌ Ошибка: {result}")


if __name__ == "__main__":
    main()