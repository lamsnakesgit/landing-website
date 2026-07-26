import paramiko
import sys

host = '151.241.100.226'
port = 22
user = 'root'
password = 'r0oLNJP3xCO7O4SnL0bj'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, password, timeout=30, banner_timeout=200)
    
    cmd = "export $(cat /root/ai_lawyer/.env | grep -v ^# | grep -v '^$' | xargs) && cd /root/ai_lawyer/kalkan_docker && docker run --rm -v /root/ai_lawyer/keys:/keys -e ECP_PASSWORD=\"$ECP_PASSWORD\" kalkan_test"
    print(f"Running command: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    
    for line in stdout:
        print(line, end="")
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
