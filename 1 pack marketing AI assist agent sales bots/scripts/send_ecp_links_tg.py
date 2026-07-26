#!/usr/bin/env python3
"""Отправка ссылок на ЭЦП ключи в Telegram"""

import urllib.request
import urllib.parse
import json

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

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
        print(f"❌ Ошибка: {e}")
        return None


def main():
    text = """🔐 *ЭЦП ключи добавлены в папку ИИ Юрист*

📂 [Открыть папку](https://drive.google.com/drive/folders/12ttgoADDaYSL27lvSSFDDoV-6dbGcUIf)

*Ключи:*
1. `GOST512_29d29484fbd0d48f561ca129fa2190b46e8592a5.p12`
   [Скачать](https://drive.google.com/file/d/1lXDYvaOJ4NOUS7GNY9TFsKtIuG1jHddy/view?usp=sharing)

2. `GOST512_2b70d42839078d60ab76e96e51be0316a12cb425.p12`
   [Скачать](https://drive.google.com/file/d/1XKBqAQMNXs1jTK1_IQDkCX1RlVnhfv5a/view?usp=sharing)

⚠️ *Внимание:* Это приватные ключи ЭЦП. Делитесь ссылками осторожно.
"""

    result = send_message(text)
    if result and result.get("ok"):
        print("✅ Сообщение отправлено")
    else:
        print(f"❌ Ошибка: {result}")


if __name__ == "__main__":
    main()