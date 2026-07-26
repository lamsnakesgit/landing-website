import paramiko

host = '151.241.100.226'
port = 22
user = 'root'
password = 'r0oLNJP3xCO7O4SnL0bj'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, password, timeout=30)
    
    cmd = "cat /root/ai_lawyer/.env | grep -i ECP"
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    for line in stdout:
        print(line, end="")
        
    ssh.close()
except Exception as e:
    print(f"Error: {e}")
