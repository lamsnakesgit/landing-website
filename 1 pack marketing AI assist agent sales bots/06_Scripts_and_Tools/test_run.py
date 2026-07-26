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
    
    cmd = "docker run --rm -v /root/ai_lawyer/keys:/keys -e ECP_PASSWORD=\"D8.891A6QzG6.\" kalkan_test"
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    
    for line in stdout:
        print(line, end="")
        
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
