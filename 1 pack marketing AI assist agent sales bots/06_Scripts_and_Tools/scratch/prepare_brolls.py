# -*- coding: utf-8 -*-
import subprocess
import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    local_broll_mp4 = "04_Design_and_Media/spy_downloads/kaisar_reel.mp4"
    local_webm_dir = "smm_brand_ai/remotion_mvp/public/video"
    local_broll_webm = os.path.join(local_webm_dir, "broll_source.webm")
    
    os.makedirs(local_webm_dir, exist_ok=True)
    
    print("1. Конвертируем оригинальный kaisar_reel.mp4 в WebM (24 fps, без звука)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", local_broll_mp4,
        "-r", "24",
        "-c:v", "libvpx",
        "-crf", "10",
        "-b:v", "2M",
        "-an",
        local_broll_webm
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Конвертация завершена: {local_broll_webm}")
    
    # Загружаем на VPS
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    print("2. Подключаемся к VPS для загрузки broll_source.webm...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    ssh.exec_command("mkdir -p /root/smm_brand_ai/remotion_mvp/public/video")
    
    sftp = ssh.open_sftp()
    remote_path = "/root/smm_brand_ai/remotion_mvp/public/video/broll_source.webm"
    print(f"Загрузка: {local_broll_webm} -> {remote_path}...")
    sftp.put(local_broll_webm, remote_path)
    sftp.close()
    ssh.close()
    print("Успешно загружено!")

if __name__ == "__main__":
    main()
