import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('151.241.100.226', username='root', password='r0oLNJP3xCO7O4SnL0bj')

stdin, stdout, stderr = client.exec_command("ls /root/ai_lawyer/kalkan_docker/output/pdfs/")
files = stdout.read().decode('utf-8').splitlines()

from collections import Counter
years = Counter()
for f in files:
    year = f.split('_')[0]
    if year.isdigit():
        years[year] += 1

print("РАСКЛАДКА ПО ГОДАМ:")
for y in sorted(years.keys(), reverse=True):
    print(f"Год {y}: {years[y]} файлов ({years[y]//2} дел)")
print(f"Всего файлов: {len(files)}")
client.close()
