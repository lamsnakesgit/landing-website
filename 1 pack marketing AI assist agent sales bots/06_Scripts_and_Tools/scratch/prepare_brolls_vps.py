# -*- coding: utf-8 -*-
import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    local_broll_mp4 = "04_Design_and_Media/spy_downloads/kaisar_reel.mp4"
    if not os.path.exists(local_broll_mp4):
        print(f"Ошибка: Локальный файл {local_broll_mp4} не найден.")
        return
        
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    print("1. Подключаемся к VPS по SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_mp4 = "/root/kaisar_reel.mp4"
    print(f"2. Загружаем {local_broll_mp4} -> {remote_mp4}...")
    sftp.put(local_broll_mp4, remote_mp4)
    sftp.close()
    
    print("3. Конвертируем MP4 в WebM (24 fps, без звука) прямо на VPS...")
    # На VPS есть мощный ffmpeg
    webm_cmd = (
        "ffmpeg -y -i /root/kaisar_reel.mp4 -r 24 -c:v libvpx -crf 10 -b:v 2M -an "
        "/root/smm_brand_ai/remotion_mvp/public/video/broll_source.webm"
    )
    
    stdin, stdout, stderr = ssh.exec_command(webm_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Конвертация на VPS успешно завершена!")
    else:
        print("Ошибка при конвертации на VPS:")
        print(stderr.read().decode("utf-8"))
        
    ssh.close()

if __name__ == "__main__":
    main()
