# -*- coding: utf-8 -*-
import paramiko
import os
import time
from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv()
    
    # 1. Скачиваем аудио/видео с VPS
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_path = "/root/kaisar_ref_hvatit_platit/kaisar_ref_selected_fixed_final.mp4"
    local_path = "scratch/temp_video.mp4"
    
    print(f"Скачиваем {remote_path} с VPS...")
    sftp.get(remote_path, local_path)
    sftp.close()
    ssh.close()
    
    print("Скачивание завершено. Загружаем в Gemini File API...")
    
    # 2. Транскрибируем через Gemini
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    video_file = client.files.upload(file=local_path)
    print(f"Файл загружен. Имя на сервере: {video_file.name}")
    
    try:
        while True:
            video_file = client.files.get(name=video_file.name)
            state = video_file.state.name
            print(f"Состояние: {state}")
            if state == "ACTIVE":
                break
            elif state == "FAILED":
                print("Ошибка обработки")
                return
            time.sleep(5)
            
        prompt = (
            "Сделай полную дословную транскрипцию этого видео на русском языке. "
            "Укажи точные таймкоды (минуты и секунды) для каждого предложения или фразы, "
            "особенно обрати внимание на отрезок от 25 до 45 секунд. "
            "Нам нужно точно локализовать фразы 'хочешь использовать ии каждый день' и 'устал сливать деньги на подрядчиков'."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt]
        )
        print("\n=== РЕЗУЛЬТАТ ТРАНСКРИПЦИИ ===")
        print(response.text)
        
    finally:
        client.files.delete(name=video_file.name)
        if os.path.exists(local_path):
            os.remove(local_path)

if __name__ == "__main__":
    main()
