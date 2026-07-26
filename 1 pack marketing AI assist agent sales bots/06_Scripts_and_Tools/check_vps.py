import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

VPS_IP = os.getenv("VPS_IP")
VPS_PASS = os.getenv("VPS_PASS")
VPS_USER = "root"

def check_vps():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    
    # Check cron
    print("=== CRON ===")
    stdin, stdout, stderr = client.exec_command('crontab -l')
    print(stdout.read().decode('utf-8'))
    
    # Check logs
    print("=== LOGS ===")
    stdin, stdout, stderr = client.exec_command('tail -n 20 /var/log/b2b_lead_system.log')
    print(stdout.read().decode('utf-8'))
    
    client.close()

if __name__ == "__main__":
    check_vps()
