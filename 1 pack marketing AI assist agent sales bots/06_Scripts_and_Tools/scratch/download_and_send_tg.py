import requests
import sys
import os

BOT_TOKEN = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
CHAT_ID = "888005446"
FILE_ID = "1tQffcQIeutV3HysRdF0KGIda6O_5dqoT"
DESTINATION = "downloaded_video.mp4"

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def download_file_from_google_drive(file_id, destination):
    print(f"Скачиваем файл с Google Drive (ID: {file_id})...")
    URL = "https://docs.google.com/uc?export=download&confirm=t"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)
    print("Скачивание завершено!")

def send_to_telegram(video_path, bot_token, chat_id):
    print(f"Отправляем видео {video_path} в Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    with open(video_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": chat_id, "caption": "Вот скачанное видео с Google Drive! 🎬"}
        response = requests.post(url, data=data, files=files)
        
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    try:
        download_file_from_google_drive(FILE_ID, DESTINATION)
        send_to_telegram(DESTINATION, BOT_TOKEN, CHAT_ID)
        # Удаляем локальный файл после отправки
        if os.path.exists(DESTINATION):
            os.remove(DESTINATION)
            print("Локальный файл удален.")
    except Exception as e:
        print("Ошибка:", e)
