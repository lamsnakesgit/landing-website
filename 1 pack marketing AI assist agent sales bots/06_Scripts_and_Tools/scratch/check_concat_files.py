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
    
    files = [
        "/root/kaisar_ref_hvatit_platit/concat_final_correct.txt",
        "/root/kaisar_ref_hvatit_platit/concat_final_trimmed.txt",
        "/root/kaisar_ref_hvatit_platit/concat_selected_fixed.txt"
    ]
    
    for f in files:
        print(f"=== File: {f} ===")
        stdin, stdout, stderr = ssh.exec_command(f"cat {f}")
        print(stdout.read().decode("utf-8"))
        print(stderr.read().decode("utf-8"))
        
    ssh.close()

if __name__ == "__main__":
    main()
