import paramiko

host = '151.241.100.226'
port = 22
user = 'root'
password = 'r0oLNJP3xCO7O4SnL0bj'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, user, password)

sftp = ssh.open_sftp()
print(sftp.listdir('/root/ai_lawyer/output'))
sftp.close()
ssh.close()
