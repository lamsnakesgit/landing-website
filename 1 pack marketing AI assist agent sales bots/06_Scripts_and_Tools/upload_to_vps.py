import paramiko
import os

host = "151.244.228.104"
port = 22
username = "root"
password = "g2AjLzx1drew4ozpArNe"
local_path = "kalkan_docker.zip"
remote_path = "/root/kalkan_docker.zip"

print(f"Подключаемся к VPS {host}...")
transport = paramiko.Transport((host, port))
transport.connect(username=username, password=password)

sftp = paramiko.SFTPClient.from_transport(transport)

print(f"Начинаю загрузку {local_path} на сервер...")
sftp.put(local_path, remote_path)

print("Загрузка успешно завершена! Файл лежит в /root/kalkan_docker.zip")

sftp.close()
transport.close()
