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
    
    # Мы проверим veo_6_ru_trimmed.mp4, veo_6_ru.mp4 и veo_7_v2.mp4
    files = ["veo_6_ru_trimmed.mp4", "veo_6_ru.mp4", "veo_7_v2.mp4"]
    
    for filename in files:
        remote_path = f"/root/kaisar_ref_hvatit_platit/{filename}"
        local_path = f"scratch/{filename}"
        
        print(f"Скачиваем {filename}...")
        try:
            sftp.get(remote_path, local_path)
            
            with open(local_path, "rb") as f:
                video_bytes = f.read()
                
            prompt = "Прослушай это видео. Звучит ли в нем фраза 'Хочешь понять, как использовать ИИ каждый день' или похожая? Ответь просто Да или Нет."
            video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[video_part, prompt]
            )
            print(f"=== {filename} содержит фразу: ===")
            print(response.text.strip())
            
        except Exception as e:
            print(f"Ошибка с {filename}: {e}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
                
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    main()
