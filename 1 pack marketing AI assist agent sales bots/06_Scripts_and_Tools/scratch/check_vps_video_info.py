# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    cmd = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration,r_frame_rate -of default=noprint_wrappers=1 /root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp.mp4"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("Video Info on VPS:")
    print(stdout.read().decode("utf-8"))
    print("Errors (if any):")
    print(stderr.read().decode("utf-8"))
    
    ssh.close()

if __name__ == "__main__":
    main()
