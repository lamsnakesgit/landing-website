import requests

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
PHOTO_PATH = "/Users/higherpower/.gemini/antigravity/brain/a64c4539-f993-40af-ac6c-36b2f9bae789/ai_agent_office_ceo_1781305421068.png"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

print(f"Отправляем фото {PHOTO_PATH}...")
try:
    with open(PHOTO_PATH, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID, 'caption': 'Вот та самая сгенерированная концепт-фотка с девушкой! 📸'}
        response = requests.post(url, data=data, files=files)
        print("Ответ от Telegram:", response.json())
except Exception as e:
    print("Ошибка отправки:", e)
