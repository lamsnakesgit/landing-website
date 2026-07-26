# -*- coding: utf-8 -*-
import paramiko
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()
    
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_video = "/root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4"
    local_video = "scratch/perfect_vps_check.mp4"
    
    print("1. Скачиваем kaisar_ref_final_perfect.mp4 с VPS...")
    sftp.get(remote_video, local_video)
    sftp.close()
    ssh.close()
    
    print("2. Читаем байты video...")
    with open(local_video, "rb") as f:
        video_bytes = f.read()
        
    prompt = "Прослушай это видео. Звучит ли в нем фраза 'Хочешь понять, как использовать ИИ каждый день'? Ответь Да или Нет."
    video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    
    print("3. Отправляем в Vertex AI...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_part, prompt]
        )
        print("\n=== РЕЗУЛЬТАТ ПРОВЕРКИ PERFECT VIDEO ===")
        print(response.text.strip())
    except Exception as e:
        print(f"Ошибка: {e}")
        
    if os.path.exists(local_video):
        os.remove(local_video)

if __name__ == "__main__":
    main()
