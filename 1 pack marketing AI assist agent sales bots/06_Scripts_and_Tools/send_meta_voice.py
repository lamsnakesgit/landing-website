#!/usr/bin/env python3
"""Генерация голосовой инструкции по получению Meta API Access Token и отправка в Telegram.
Токен бота берётся из переменной окружения ANTIGRAVITY_BOT_TOKEN,
ID чата – из TG_CHAT_ID_MAIN.
Требуются пакеты: edge_tts, ffmpeg (доступен в PATH).
"""
import os, subprocess, sys, json, asyncio
from pathlib import Path
import edge_tts

# Текст инструкции (русский)
INSTRUCTION = """
Инструкция по получению Meta API Access Token для сервиса Postiz:
1. Зарегистрировать приложение в Meta for Developers, получить App ID и App Secret.
2. Сгенерировать короткий пользовательский токен через Graph API Explorer.
3. Обменять короткий токен на долгосрочный запросом GET к https://graph.facebook.com/v17.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_TOKEN}.
4. Получить Page Access Token для вашей страницы запросом GET к https://graph.facebook.com/v17.0/{PAGE_ID}?fields=access_token&access_token={LONG_LIVED_USER_TOKEN}.
5. Телефонная верификация обязательна при создании бизнес‑аккаунта и её нельзя обойти.
"""

# Параметры TTS
VOICE = "ru-RU-SvetlanaNeural"
RATE = "+2%"
MP3_PATH = Path("meta_instr.mp3")
OGG_PATH = Path("meta_instr.ogg")

async def make_mp3():
    communicate = edge_tts.Communicate(text=INSTRUCTION, voice=VOICE, rate=RATE)
    await communicate.save(str(MP3_PATH))

asyncio.run(make_mp3())

# Конвертация MP3 -> OGG (opus) для voice note
subprocess.run(["ffmpeg", "-y", "-i", str(MP3_PATH), "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", str(OGG_PATH)], check=True)

# Отправка voice note в Telegram
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID_MAIN")
if not BOT_TOKEN or not CHAT_ID:
    sys.exit("Missing TG bot token or chat id in environment")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
# Use curl for simplicity
subprocess.run([
    "curl", "-s", "-X", "POST", url,
    "-F", f"chat_id={CHAT_ID}",
    "-F", f"caption=Meta API токен инструкция",
    "-F", f"voice=@{OGG_PATH}"
], check=True)
print("Voice note sent to Telegram")
