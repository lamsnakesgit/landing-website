# -*- coding: utf-8 -*-
import os
import sys
import paramiko
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()
    
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    
    print("Инициализация клиента Vertex AI...")
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    # Скачиваем последнее смонтированное видео с VPS
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_video = "/root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4"
    local_video = "scratch/vps_final_perfect.mp4"
    
    print(f"Скачиваем {remote_video}...")
    sftp.get(remote_video, local_video)
    sftp.close()
    ssh.close()
    
    # Читаем видео в байты
    print("Читаем байты видео...")
    with open(local_video, "rb") as f:
        video_bytes = f.read()
        
    prompt = (
        "Сделай полный аудит этого видеоролика на русском языке:\n"
        "1. Полный дословный транскрипт речи с таймкодами.\n"
        "2. Описание происходящего на экране (визуальный ряд, переходы, B-roll перебивки, появление титров).\n"
        "3. Внимательно найди все места (таймкоды), где на видео появляется текст на русском языке (кириллица), "
        "который выглядит криво, искаженно, содержит ошибки или артефакты генерации. "
        "Для каждого такого случая укажи точный таймкод (секунды), что там написано не так и как это нужно замазать плашкой и написать чистым текстом.\n"
        "4. Соответствует ли финальный результат ТЗ: 'Устал сливать бюджеты на подрядчиков? Запусти свой ИИ контент-завод! Пиши слово ВИДЕО в директ, и я скину тебе подробный гайд.'\n"
        "5. Выяви любые баги: рассинхронизация звука и видео, артефакты генерации лица, обрубки слов."
    )
    
    video_part = types.Part.from_bytes(
        data=video_bytes,
        mime_type="video/mp4"
    )
    
    # Используем проверенный gemini-2.5-flash
    model_name = "gemini-2.5-flash"
    print(f"Отправляем запрос в Vertex AI c моделью {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[video_part, prompt]
        )
        print(f"\n=== ПОЛНЫЙ АУДИТ ВИДЕО (Модель: {model_name}) ===")
        print(response.text)
        
        # Сохраняем аудит в файл
        audit_file = "docs/video_audit_report.md"
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write(f"# Отчет об аудите смонтированного видео ({model_name})\n\n")
            f.write(response.text)
        print(f"\nОтчет сохранен в {audit_file}")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        
    if os.path.exists(local_video):
        os.remove(local_video)

if __name__ == "__main__":
    main()
