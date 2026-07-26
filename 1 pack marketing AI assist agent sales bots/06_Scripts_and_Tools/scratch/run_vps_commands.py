# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv

def run_cmd(ssh, cmd):
    print(f"\n--- Running: {cmd} ---")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # Считываем построчно
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            rl = stdout.channel.recv(1024).decode("utf-8")
            print(rl, end="")
            
    # Дочитываем оставшееся
    print(stdout.read().decode("utf-8"), end="")
    err = stderr.read().decode("utf-8")
    if err:
        print(f"Error output:\n{err}")
        
    print(f"Exit code: {stdout.channel.recv_exit_status()}")

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    # Шаг 1: Конвертируем background разговорного клона (ИСПОЛЬЗУЕМ КОРРЕКТНЫЙ kaisar_ref_final_perfect.mp4 БЕЗ ЛИШНЕЙ ФРАЗЫ)
    run_cmd(ssh, "ffmpeg -y -i /root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4 -c:v libvpx -crf 10 -b:v 2M -c:a libvorbis /root/smm_brand_ai/remotion_mvp/public/video/background.webm")
    
    # Шаг 2: npm install
    run_cmd(ssh, "cd /root/smm_brand_ai/remotion_mvp && npm install")
    
    # Шаг 3: npm run render
    run_cmd(ssh, "cd /root/smm_brand_ai/remotion_mvp && npm run render")
    
    # Шаг 4: faststart оптимизация
    run_cmd(ssh, "ffmpeg -y -i /root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp.mp4 -c:v libx264 -preset fast -crf 22 -c:a aac -movflags +faststart /root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp_faststart.mp4")
    
    ssh.close()

if __name__ == "__main__":
    main()
