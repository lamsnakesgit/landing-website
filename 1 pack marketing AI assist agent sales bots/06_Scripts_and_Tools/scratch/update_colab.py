# 0. Сбрасываем рабочую директорию в корень Colab для избежания вложенности
%cd /content

# 1. Принудительно убиваем любые зависшие процессы на порту 8188 перед запуском
!fuser -k 8188/tcp || true

# 2. Клонируем репозиторий ComfyUI (если еще не склонирован)
import os
if not os.path.exists('ComfyUI'):
    !git clone https://github.com/comfyanonymous/ComfyUI.git
%cd ComfyUI

# 3. Устанавливаем официальный ComfyUI Manager через pip в среду Colab
!pip install -U --pre comfyui-manager
!pip install -r requirements.txt

# 4. Устанавливаем плагин IP-Adapter Plus (cubiq) в custom_nodes
%cd custom_nodes
if not os.path.exists('ComfyUI_IPAdapter_plus'):
    !git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
%cd ..

# 5. Скачиваем модели (SDXL + IP-Adapter) если их нет
!wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors -P models/checkpoints/
!mkdir -p models/ipadapter
!wget -c https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors -P models/ipadapter/

# 6. Скачиваем и устанавливаем Cloudflare Tunnel через deb пакет
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
!dpkg -i cloudflared-linux-amd64.deb

# 7. Запуск туннелирования в фоновом потоке с проверкой сокета
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
    
    print("\n[Туннель] ComfyUI успешно запущен! Подключаем туннель Cloudflare...\n")
    p = subprocess.Popen(["cloudflared", "tunnel", "--protocol", "http2", "--url", "http://127.0.0.1:{}".format(port)], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for line in p.stderr:
        l = line.decode()
        if "trycloudflare.com" in l and "https://" in l:
            idx = l.find("https://")
            url = l[idx:].strip().split(" ")[0].strip("|").strip()
            print("\n\n🔥 ВАША ССЫЛКА НА COMFYUI: " + url + "\n\n")
            break

# Запускаем поток туннелирования в фоне
threading.Thread(target=tunnel_thread, daemon=True, args=(8188,)).start()

# 8. Запускаем ComfyUI на переднем плане с менеджером и CORS
print("\n[Сервер] Запуск ComfyUI с поддержкой Manager...")
!python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header --enable-manager --dont-print-server
