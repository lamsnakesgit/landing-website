# -*- coding: utf-8 -*-
import paramiko
import os
import sys
import cv2
import base64
import glob
import json
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # 1. Подключаемся к VPS и скачиваем kaisar_ref_final_perfect.mp4
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_path = "/root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4"
    local_path = "scratch/vps_final_perfect.mp4"
    
    print(f"Скачиваем {remote_path}...")
    if os.path.exists(local_path):
        os.remove(local_path)
    sftp.get(remote_path, local_path)
    sftp.close()
    ssh.close()
    
    # 2. Нарезаем кадры (1 кадр в секунду)
    print("Нарезаем кадры из видео...")
    frames_dir = "scratch/frames"
    os.makedirs(frames_dir, exist_ok=True)
    # Очищаем папку кадров
    for f in glob.glob(f"{frames_dir}/*.jpg"):
        os.remove(f)
        
    cam = cv2.VideoCapture(local_path)
    fps = cam.get(cv2.CAP_PROP_FPS)
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    print(f"FPS: {fps:.2f}, Кадров: {total_frames}, Длительность: {duration:.2f} сек")
    
    frame_count = 0
    saved_count = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        # Берем один кадр каждую секунду
        if frame_count % int(round(fps)) == 0:
            sec = int(round(frame_count / fps))
            frame_name = f"{frames_dir}/frame_{sec:03d}.jpg"
            cv2.imwrite(frame_name, frame)
            saved_count += 1
        frame_count += 1
    cam.release()
    print(f"Сохранено {saved_count} кадров для анализа.")
    
    # 3. Отбираем кадры и кодируем в base64
    frame_files = sorted(glob.glob(f"{frames_dir}/*.jpg"))
    
    # Формируем запрос к ИИ (GPT-4o через AIHubMix)
    api_key = os.getenv("AIHUBMIX_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY").rstrip('.')
        
    url = "https://api.aihubmix.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Подготавливаем контент с текстом и картинками
    # Передаем кадры через один, чтобы не превысить лимиты токенов
    messages_content = [
        {
            "type": "text",
            "text": (
                "Перед тобой раскадровка (1 кадр в секунду) смонтированного видеоролика. "
                "Твоя задача — внимательно отсмотреть каждый кадр на предмет поехавшего/искаженного русского текста (кириллицы), "
                "который сгенерировал ИИ (Veo). Текст может быть размытым, содержать странные символы, опечатки или сливаться.\n\n"
                "Для каждого проблемного кадра укажи:\n"
                "1. Время (секунда из названия файла frame_XXX.jpg).\n"
                "2. Какая фраза или надпись отображается с ошибкой/искажением.\n"
                "3. Каким чистым русским текстом ее нужно заменить/перекрыть.\n"
                "4. Координаты или зона на экране (например, верхняя треть, центр, нижняя треть).\n\n"
                "Верни результат в формате JSON списка объектов с ключами: 'time_sec', 'bad_text', 'correct_text', 'position' (top/center/bottom)."
            )
        }
    ]
    
    for idx, fpath in enumerate(frame_files):
        # Отправляем кадры с интервалом в 2 секунды (каждый второй), чтобы сэкономить токены и уложиться в контекст
        if idx % 2 == 0:
            with open(fpath, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            messages_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
            
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": messages_content
            }
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 2000
    }
    
    print("Отправляем кадры на визуальный аудит в GPT-4o-mini...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        text_response = result['choices'][0]['message']['content']
        print("\n=== РЕЗУЛЬТАТ АУДИТА ===")
        print(text_response)
        
        # Сохраняем аудит в JSON
        with open("scratch/visual_audit.json", "w", encoding="utf-8") as f:
            f.write(text_response)
    else:
        print("Ошибка запроса к ИИ:", response.status_code)
        print(response.text)
        
    # Очистка
    if os.path.exists(local_path):
        os.remove(local_path)
    for f in glob.glob(f"{frames_dir}/*.jpg"):
        os.remove(f)
    os.rmdir(frames_dir)

if __name__ == "__main__":
    main()
