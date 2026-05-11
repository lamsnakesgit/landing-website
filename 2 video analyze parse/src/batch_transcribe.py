import os
import subprocess
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/batch_processing.log"),
        logging.StreamHandler()
    ]
)

VIDEO_DIR = "/Users/higherpower/Downloads/магия гугл 2 7 модуль 5 веб аналитика"
SCRIPT_PATH = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 video analyze parse/src/transcriber.py"

def process_all_videos():
    if not os.path.exists(VIDEO_DIR):
        logging.error(f"Папка с видео не найдена: {VIDEO_DIR}")
        return

    files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
    files.sort() # Для порядка уроков

    logging.info(f"[*] Найдено {len(files)} видео для обработки.")

    for i, file_name in enumerate(files, 1):
        file_path = os.path.join(VIDEO_DIR, file_name)
        logging.info(f"[*] Обработка урока {i}/{len(files)}: {file_name}")
        
        try:
            # Запускаем transcriber.py для каждого файла
            result = subprocess.run(
                ["python3", SCRIPT_PATH, file_path],
                capture_output=True,
                text=True,
                check=True
            )
            if "SUCCESS" in result.stdout:
                logging.info(f"[+] Урок {i} завершен успешно.")
            else:
                logging.error(f"[!] Урок {i} завершен с ошибкой: {result.stderr}")
        except Exception as e:
            logging.error(f"[!] Критическая ошибка при обработке {file_name}: {e}")

if __name__ == "__main__":
    process_all_videos()
