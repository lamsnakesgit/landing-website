import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('151.241.100.226', username='root', password='r0oLNJP3xCO7O4SnL0bj')

sftp = client.open_sftp()
sftp.get('/root/ai_lawyer/kalkan_docker/sud_parser.py', 'sud_parser_vps.py')
sftp.close()
client.close()
