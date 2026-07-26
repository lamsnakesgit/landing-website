#!/usr/bin/env python3
"""Уведомление о безопасности ЭЦП ключей"""

import urllib.request
import urllib.parse
import json

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

def send_message(text):
    data = urllib.parse.urlencode({
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }).encode('utf-8')
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data, method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ {e}")
        return None

text = """🔐 *Обновление безопасности*

ЭЦП ключи в папке "ИИ Юрист" теперь **приватные**:
- Доступ только через твой Google аккаунт
- Публичные ссылки отключены

*В папке:*
• 7 PDF-файлов (публичные, ссылки работают)
• 2 ЭЦП ключа GOST512 (приватные, только для тебя)

📂 [Открыть папку](https://drive.google.com/drive/folders/12ttgoADDaYSL27lvSSFDDoV-6dbGcUIf)

⚙️ Настроено автоопределение: файлы `.p12`, `.pfx`, `.jks`, `.pem`, `.key`, `.cer`, `.crt` загружаются без публичного доступа.
"""

result = send_message(text)
print("✅ Отправлено" if result and result.get("ok") else f"❌ Ошибка: {result}")