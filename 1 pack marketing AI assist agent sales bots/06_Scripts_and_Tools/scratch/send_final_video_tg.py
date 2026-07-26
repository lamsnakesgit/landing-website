# -*- coding: utf-8 -*-
import paramiko
import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    
    print("1. Скачиваем финальный отрендеренный ролик с VPS...")
    remote_rendered_video = "/root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp_faststart.mp4"
    local_rendered_video = "scratch/episode_01_remotion_mvp_final.mp4"
    
    if os.path.exists(local_rendered_video):
        os.remove(local_rendered_video)
    sftp.get(remote_rendered_video, local_rendered_video)
    
    sftp.close()
    ssh.close()
    
    print("2. Отправляем ролик в Telegram с корректными размерами (720x1280, 49s)...")
    bot_token = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
    chat_id = "888005446"
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    caption = "Ваш готовый Reels со встроенными B-roll сценами и последовательными субтитрами! 🚀"
    with open(local_rendered_video, "rb") as video:
        files = {"video": video}
        data = {
            "chat_id": chat_id, 
            "caption": caption,
            "width": 720,
            "height": 1280,
            "duration": 49,
            "supports_streaming": True
        }
        response = requests.post(url, data=data, files=files)
        
    print("Статус отправки в Telegram:", response.status_code)
    print("Ответ Telegram:", response.text[:500])
    
    if os.path.exists(local_rendered_video):
        os.remove(local_rendered_video)

if __name__ == "__main__":
    main()
