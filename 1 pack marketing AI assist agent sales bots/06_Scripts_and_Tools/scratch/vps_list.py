# -*- coding: utf-8 -*-
import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    print(f"Подключение к VPS: {ip}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    cmd = "ls -la /root/kaisar_ref_hvatit_platit"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("Files on VPS:")
    print(stdout.read().decode("utf-8"))
    print("Errors:")
    print(stderr.read().decode("utf-8"))
    
    ssh.close()

if __name__ == "__main__":
    main()
