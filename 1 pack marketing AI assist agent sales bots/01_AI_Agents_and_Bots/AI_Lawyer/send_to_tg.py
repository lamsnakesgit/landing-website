import requests
import os
from gtts import gTTS

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
MD_FILE = "docs/learn/system_architecture.md"
MP3_FILE = "/tmp/system_architecture.mp3"

# 1. Read MD file
with open(MD_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# 2. Generate TTS
print("Generating TTS...")
tts = gTTS(text, lang='ru')
tts.save(MP3_FILE)

# 3. Send Document
print("Sending document...")
doc_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
with open(MD_FILE, "rb") as f:
    res = requests.post(doc_url, data={"chat_id": CHAT_ID, "caption": "📚 Документация: Архитектура Второго Мозга"}, files={"document": f})
    print(res.json())

# 4. Send Audio
print("Sending audio...")
audio_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
with open(MP3_FILE, "rb") as f:
    res = requests.post(audio_url, data={"chat_id": CHAT_ID, "caption": "🎧 Озвучка: Архитектура Второго Мозга"}, files={"audio": f})
    print(res.json())

print("Done!")
