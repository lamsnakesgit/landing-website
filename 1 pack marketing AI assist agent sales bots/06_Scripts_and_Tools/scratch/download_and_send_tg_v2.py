import requests
import sys
import os
import re
import subprocess

BOT_TOKEN = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
CHAT_ID = "888005446"
FILE_ID = "1tQffcQIeutV3HysRdF0KGIda6O_5dqoT"
RAW_FILE = "raw_video.mp4"
COMPRESSED_FILE = "compressed_video.mp4"

def download_file_from_google_drive(file_id, destination):
    print(f"Запрос страницы подтверждения Google Drive (ID: {file_id})...")
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    page_response = session.get(URL, params={'id': file_id})
    
    # Парсим URL действия формы
    action_match = re.search(r'action="([^"]+)"', page_response.text)
    action_url = action_match.group(1) if action_match else "https://drive.usercontent.google.com/download"
    
    # Парсим скрытые параметры (включая динамический uuid)
    inputs = re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]+)"', page_response.text)
    params = {name: val for name, val in inputs}
    
    if not params:
        print("Форма подтверждения не найдена. Возможно, файл общедоступен без предупреждения.")
        params = {'id': file_id, 'export': 'download'}
        action_url = URL

    print(f"Начинаем скачивание файла по ссылке {action_url} с параметрами {params}...")
    response = session.get(action_url, params=params, stream=True)

    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                
    size_mb = os.path.getsize(destination) / (1024 * 1024)
    print(f"Скачивание завершено! Размер файла: {size_mb:.2f} MB")
    return size_mb

def compress_video(input_path, output_path):
    print("Файл больше 50 MB. Запускаем сжатие видео через ffmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vcodec", "libx264",
        "-crf", "28",
        "-preset", "fast",
        "-acodec", "aac",
        "-b:a", "128k",
        output_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Ошибка ffmpeg: {result.stderr.decode('utf-8')}")
        
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Сжатие завершено! Новый размер: {size_mb:.2f} MB")
    return size_mb

def send_to_telegram(video_path, bot_token, chat_id, caption="Вот ваше видео! 🎬"):
    print(f"Отправляем видео {video_path} в Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    with open(video_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": chat_id, "caption": caption}
        response = requests.post(url, data=data, files=files)
        
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    try:
        raw_size = download_file_from_google_drive(FILE_ID, RAW_FILE)
        
        file_to_send = RAW_FILE
        caption = "Вот видео с Google Drive! 🎬"
        
        if raw_size >= 50.0:
            compress_video(RAW_FILE, COMPRESSED_FILE)
            file_to_send = COMPRESSED_FILE
            caption = f"Видео сжато для обхода лимита Telegram 50MB (Оригинал: {raw_size:.1f}MB) 🎬"
            
        send_to_telegram(file_to_send, BOT_TOKEN, CHAT_ID, caption)
        
        # Очистка
        for f in [RAW_FILE, COMPRESSED_FILE]:
            if os.path.exists(f):
                os.remove(f)
        print("Временные файлы удалены.")
    except Exception as e:
        print("Произошла ошибка:", e)
        # Очистка в случае ошибки
        for f in [RAW_FILE, COMPRESSED_FILE]:
            if os.path.exists(f):
                os.remove(f)
