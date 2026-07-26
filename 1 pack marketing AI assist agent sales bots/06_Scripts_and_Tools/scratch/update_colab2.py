# 0. Сбрасываем рабочую директорию в корень Colab для избежания вложенности
%cd /content

# 1. Принудительно убиваем любые зависшие процессы на порту 8188 перед запуском
!fuser -k 8188/tcp || true

# 2. Клонируем репозиторий ComfyUI (если еще не склонирован)
import os
if not os.path.exists('ComfyUI'):
    !git clone https://github.com/comfyanonymous/ComfyUI.git
%cd ComfyUI

# 3. Устанавливаем легкие зависимости
!pip install -r requirements.txt

# 4. Скачиваем модели (SDXL + IP-Adapter) если их нет
!wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors -P models/checkpoints/
!mkdir -p models/ipadapter
!wget -c https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors -P models/ipadapter/

# 5. Устанавливаем localtunnel через npm
!npm install -g localtunnel

# 6. Получаем IP-адрес Colab-машины (он нужен как пароль для входа в localtunnel)
print("\n🔑 ПАРОЛЬ (IP) ДЛЯ ВХОДА В LOCALTUNNEL:")
!curl ipv4.icanhazip.com
print("Скопируй этот IP-адрес. При переходе по ссылке вставь его в поле 'Click to Submit' / 'Tunnel Password'.\n")

# 7. Запуск туннелирования localtunnel в фоновом потоке с проверкой сокета
import subprocess
import threading
import time
import socket

def tunnel_thread(port):
    print("\n[Туннель] Ожидаем запуск веб-сервера ComfyUI на порту {}...\n".format(port))
    while True:
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            break
        sock.close()
    
    print("\n[Туннель] ComfyUI успешно запущен! Подключаем туннель Localtunnel...\n")
    p = subprocess.Popen(["lt", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # lt пишет ссылку в stdout
    for line in p.stdout:
        l = line.decode()
        if "your url is" in l:
            url = l.split("your url is:")[1].strip()
            print("\n\n🔥 ВАША ССЫЛКА НА COMFYUI: " + url + "\n\n")
            break

# Запускаем поток туннелирования в фоне
threading.Thread(target=tunnel_thread, daemon=True, args=(8188,)).start()

# 8. Запускаем ComfyUI на переднем плане с биндингом на 127.0.0.1
print("\n[Сервер] Запуск ComfyUI...")
!python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header --dont-print-server
