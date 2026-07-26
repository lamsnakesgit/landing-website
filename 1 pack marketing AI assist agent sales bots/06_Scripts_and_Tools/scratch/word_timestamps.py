# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv
import openai

def main():
    load_dotenv()
    
    # 1. Подключаемся к VPS и скачиваем veo_5_ru.mp4
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_path = "/root/kaisar_ref_hvatit_platit/veo_5_ru.mp4"
    local_path = "scratch/veo_5_ru.mp4"
    
    print(f"Скачиваем {remote_path}...")
    sftp.get(remote_path, local_path)
    sftp.close()
    ssh.close()
    
    # 2. Извлекаем аудио
    audio_path = "scratch/veo_5_ru.mp3"
    if os.path.exists(audio_path):
        os.remove(audio_path)
    os.system(f"ffmpeg -y -i {local_path} -vn -acodec libmp3lame -ar 16000 -ac 1 {audio_path} > /dev/null 2>&1")
    
    # 3. Инициализируем клиента для AIHubMix
    api_key = os.getenv("AIHUBMIX_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY").rstrip('.')
        
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.aihubmix.com/v1"
    )
    
    print("Отправляем в Whisper (AIHubMix) для пословных таймкодов...")
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
        
        print("\n=== ПОСЛОВНЫЕ ТАЙМКОДЫ ДЛЯ veo_5_ru.mp4 ===")
        for word_info in transcript.words:
            # Обрабатываем как объект
            print(f"[{word_info.start:.3f}s - {word_info.end:.3f}s]: {word_info.word}")
            
    except Exception as e:
        print("Ошибка запроса:", str(e))
        
    # Очищаем временные файлы
    if os.path.exists(local_path):
        os.remove(local_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)

if __name__ == "__main__":
    main()
