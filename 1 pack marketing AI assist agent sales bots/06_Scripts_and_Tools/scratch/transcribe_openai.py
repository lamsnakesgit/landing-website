# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv
import openai

def main():
    load_dotenv()
    
    # 1. Подключаемся к VPS и скачиваем нужные видеофайлы для анализа
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    
    # Мы хотим проанализировать veo_4_ru.mp4, veo_5_ru.mp4, veo_6_ru.mp4
    files_to_transcribe = ["veo_4_ru.mp4", "veo_5_ru.mp4", "veo_6_ru.mp4"]
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    
    for filename in files_to_transcribe:
        remote_path = f"/root/kaisar_ref_hvatit_platit/{filename}"
        local_path = f"scratch/{filename}"
        
        print(f"Скачиваем {remote_path}...")
        sftp.get(remote_path, local_path)
        
        # Извлекаем аудио через ffmpeg локально
        audio_path = f"scratch/{filename}.mp3"
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        print(f"Извлекаем аудио для {filename}...")
        os.system(f"ffmpeg -y -i {local_path} -vn -acodec libmp3lame -ar 16000 -ac 1 {audio_path} > /dev/null 2>&1")
        
        print(f"Отправляем в OpenAI Whisper для {filename}...")
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            
        print(f"=== Транскрипт для {filename} ===")
        for segment in transcript.segments:
            print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
            
        # Удаляем временные локальные файлы
        os.remove(local_path)
        os.remove(audio_path)
        
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    main()
