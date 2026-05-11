import os
import whisper
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/transcription.log"),
        logging.StreamHandler()
    ]
)

def transcribe_video(file_path, model_name="base"):
    """
    Транскрибирует видеофайл с помощью OpenAI Whisper
    """
    if not os.path.exists(file_path):
        logging.error(f"Файл не найден: {file_path}")
        return None

    logging.info(f"[*] Начало транскрибации: {file_path} (модель: {model_name})")
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path, language="ru")
        logging.info(f"[+] Транскрибация завершена успешно: {file_path}")
        return result["text"]
    except Exception as e:
        logging.error(f"[!] Ошибка при транскрибации {file_path}: {e}")
        return None

def save_to_local_txt(text, video_name, output_dir="downloads/transcripts"):
    """
    Сохраняет текст в локальный файл (как бэкап перед GDocs)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{video_name}_{timestamp}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    logging.info(f"[+] Текст сохранен локально: {file_path}")
    return file_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        video_base_name = os.path.basename(video_path)
        
        text_result = transcribe_video(video_path)
        if text_result:
            save_to_local_txt(text_result, video_base_name)
            # В будущем здесь будет вызов Google Docs интеграции
            print(f"SUCCESS: {video_base_name}")
            print(text_result[:200] + "...") # Вывод начала текста для проверки
        else:
            print(f"FAILED: {video_base_name}")
    else:
        print("Использование: python3 src/transcriber.py <путь_к_видео>")
