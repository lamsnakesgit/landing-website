# -*- coding: utf-8 -*-
import os
import sys
import time
import paramiko
from dotenv import load_dotenv
from google import genai

def main():
    load_dotenv()
    
    # 1. Параметры Vertex AI
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    
    # Инициализируем клиент Vertex AI
    print("Инициализация клиента Vertex AI...")
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    # 2. Скачиваем последнее смонтированное видео с VPS для анализа
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    sftp = ssh.open_sftp()
    remote_video = "/root/kaisar_ref_hvatit_platit/kaisar_ref_selected_fixed_final_trimmed.mp4"
    local_video = "scratch/vps_final_trimmed.mp4"
    
    print(f"Скачиваем {remote_video}...")
    sftp.get(remote_video, local_video)
    sftp.close()
    ssh.close()
    
    # 3. Загружаем видео в Vertex AI / Gemini File API
    print("Загружаем видео в Gemini File API via Vertex...")
    # Примечание: Для Vertex AI загрузка файлов может идти через GCS или напрямую в зависимости от SDK.
    # В новом Google GenAI SDK client.files.upload работает прозрачно.
    video_file = client.files.upload(file=local_video)
    print(f"Файл загружен: {video_file.name}")
    
    try:
        while True:
            video_file = client.files.get(name=video_file.name)
            state = video_file.state.name
            print(f"Состояние видео: {state}")
            if state == "ACTIVE":
                break
            elif state == "FAILED":
                print("Ошибка обработки видео")
                sys.exit(1)
            time.sleep(5)
            
        print("Анализируем видеоролик...")
        prompt = (
            "Сделай полный аудит этого видеоролика на русском языке:\n"
            "1. Полный дословный транскрипт речи с таймкодами.\n"
            "2. Описание происходящего на экране (визуальный ряд, переходы, B-roll перебивки, появление титров).\n"
            "3. Оценка динамики ролика: не затянут ли он, хорошая ли скорость склеек.\n"
            "4. Соответствует ли финальный результат ТЗ: 'Устал сливать бюджеты на подрядчиков? Запусти свой ИИ контент-завод! Пиши слово ВИДЕО в директ, и я скину тебе подробный гайд.'\n"
            "5. Выяви любые баги: рассинхронизация звука и видео, артефакты генерации лица, обрубки слов."
        )
        
        # Используем модель gemini-1.5-flash (или gemini-1.5-pro/gemini-2.5-flash)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[video_file, prompt]
        )
        
        print("\n=== ПОЛНЫЙ АУДИТ ВИДЕО ===")
        print(response.text)
        
        # Сохраняем аудит в файл
        audit_file = "docs/video_audit_report.md"
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write("# Отчет об аудите смонтированного видео\n\n")
            f.write(response.text)
        print(f"\nОтчет сохранен в {audit_file}")
        
    finally:
        print("Удаляем временные файлы...")
        client.files.delete(name=video_file.name)
        if os.path.exists(local_video):
            os.remove(local_video)

if __name__ == "__main__":
    main()
