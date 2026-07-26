import paramiko
import sys

host = "151.241.100.226"
password = "r0oLNJP3xCO7O4SnL0bj"
user = "root"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting...")
ssh.connect(host, username=user, password=password)

print("Opening SFTP...")
sftp = ssh.open_sftp()
local_path = "ai_lawyer/документы_юрист 4000 в 10_/merged_0001.txt"
remote_path = "/root/merged_0001.txt"
print("Uploading...")
sftp.put(local_path, remote_path)
sftp.close()

print("File uploaded. Setting up HTTP server...")
stdin, stdout, stderr = ssh.exec_command("killall python3; nohup python3 -m http.server 80 > /dev/null 2>&1 &")
print("Done!")
