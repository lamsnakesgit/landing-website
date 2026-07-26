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
    
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'node|ffmpeg|remotion'")
    print("Processes on VPS:")
    print(stdout.read().decode("utf-8"))
    
    ssh.close()

if __name__ == "__main__":
    main()
