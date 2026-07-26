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
    
    for filename in ["make_speed_13.sh", "make_trimmed_speed_13.sh", "concat_selected_fixed.txt", "concat_speed_13_trimmed.txt"]:
        print(f"=== {filename} ===")
        stdin, stdout, stderr = ssh.exec_command(f"cat /root/kaisar_ref_hvatit_platit/{filename}")
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))
        
    ssh.close()

if __name__ == "__main__":
    main()
