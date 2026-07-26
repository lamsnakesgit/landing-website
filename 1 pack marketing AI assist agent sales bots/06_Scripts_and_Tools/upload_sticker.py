import os
import requests
import time

def upload_sticker_pack(bot_token, user_id, pack_name, pack_title, sticker_path):
    print("Начинаем процесс загрузки стикер-пака через Telegram API...")
    
    # URL для API
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    # 1. Загружаем файл на сервера Telegram (uploadStickerFile)
    print(f"Загружаем файл {sticker_path}...")
    with open(sticker_path, 'rb') as f:
        response = requests.post(
            f"{base_url}/uploadStickerFile",
            data={'user_id': user_id, 'sticker_format': 'static'},
            files={'sticker': f}
        )
    
    if not response.json().get('ok'):
        print(f"Ошибка загрузки файла: {response.json()}")
        return

    file_id = response.json()['result']['file_id']
    print(f"Файл успешно загружен! ID файла: {file_id}")
    
    # 2. Создаем новый стикер-пак (createNewStickerSet)
    print(f"Создаем стикер-пак '{pack_title}'...")
    
    stickers_data = '[{"sticker": "' + file_id + '", "emoji_list": ["💰", "🤖"]}]'
    
    response = requests.post(
        f"{base_url}/createNewStickerSet",
        data={
            'user_id': user_id,
            'name': pack_name,
            'title': pack_title,
            'stickers': stickers_data,
            'sticker_format': 'static'
        }
    )
    
    if response.json().get('ok'):
        print("✅ Стикер-пак успешно создан!")
        print(f"👉 Ссылка на твой пак: https://t.me/addstickers/{pack_name}")
    else:
        err = response.json()
        print(f"❌ Ошибка создания пака: {err}")
        if "name_invalid" in str(err) or "TAKEN" in str(err):
            print("Попробуй другое уникальное имя (pack_name). Оно должно обязательно заканчиваться на _by_ИмяТвоегоБота")

if __name__ == "__main__":
    print("🤖 Загрузчик стикер-паков в Telegram")
    print("-" * 40)
    BOT_TOKEN = input("Введи токен твоего бота (BotFather): ").strip()
    USER_ID = input("Введи твой Telegram User ID (можно узнать через @userinfobot): ").strip()
    
    # Имя пака должно заканчиваться на _by_<bot_username>
    bot_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe").json()
    if not bot_info.get('ok'):
        print("Неверный токен бота!")
        exit()
        
    bot_username = bot_info['result']['username']
    PACK_NAME = f"ai_sales_pack_{int(time.time())}_by_{bot_username}"
    PACK_TITLE = "AI Sales Agent Pack 🤖💰"
    STICKER_FILE = "sticker_01.png"
    
    upload_sticker_pack(BOT_TOKEN, USER_ID, PACK_NAME, PACK_TITLE, STICKER_FILE)
