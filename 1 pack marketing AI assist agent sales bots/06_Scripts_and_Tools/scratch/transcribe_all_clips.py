# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv
import openai

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    
    # Список файлов для проверки
    filenames = ["veo_2_fixed.mp4", "veo_3_fixed.mp4", "veo_4_ru.mp4", "veo_5_ru.mp4", "veo_6_ru.mp4", "veo_7_v2.mp4", "final_scene_1.mp4"]
    
    api_key = os.getenv("AIHUBMIX_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY").rstrip('.')
        
    client = openai.OpenAI(api_key=api_key, base_url="https://api.aihubmix.com/v1")
    
    for filename in filenames:
        remote_path = f"/root/kaisar_ref_hvatit_platit/{filename}"
        local_path = f"scratch/trans_{filename}"
        audio_path = f"scratch/trans_{filename}.mp3"
        
        try:
            print(f"Скачиваем {filename}...")
            sftp.get(remote_path, local_path)
            
            # Извлекаем аудио
            os.system(f"ffmpeg -y -i {local_path} -vn -acodec libmp3lame -ar 16000 -ac 1 {audio_path} > /dev/null 2>&1")
            
            # Whisper
            with open(audio_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            print(f"\n=== {filename} ===")
            for word_info in transcript.words:
                print(f"[{word_info.start:.3f}s - {word_info.end:.3f}s]: {word_info.word}")
                
        except Exception as e:
            print(f"Ошибка с файлом {filename}: {str(e)}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    main()
