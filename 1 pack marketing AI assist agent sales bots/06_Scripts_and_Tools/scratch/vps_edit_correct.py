# -*- coding: utf-8 -*-
import paramiko
import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    ip = os.getenv("VPS_IP")
    password = os.getenv("VPS_PASS")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password=password)
    
    print("1. Обрезаем veo_6_ru.mp4 на VPS (оставляем только 0.0s - 3.8s, убираем фразу про 'Хочешь понять как использовать ИИ')...")
    trim_cmd = (
        "ffmpeg -y -i /root/kaisar_ref_hvatit_platit/veo_6_ru.mp4 "
        "-to 3.8 -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k "
        "/root/kaisar_ref_hvatit_platit/veo_6_ru_trimmed.mp4"
    )
    stdin, stdout, stderr = ssh.exec_command(trim_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при обрезке veo_6_ru:")
        print(stderr.read().decode("utf-8"))
        ssh.close()
        return
        
    print("2. Создаем файл списков для корректной склейки на VPS...")
    concat_list = (
        "file 'final_scene_1.mp4'\n"
        "file 'veo_2_fixed.mp4'\n"
        "file 'veo_3_fixed.mp4'\n"
        "file 'veo_4_ru.mp4'\n"
        "file 'veo_5_ru.mp4'\n"
        "file 'veo_6_ru_trimmed.mp4'\n"
        "file 'veo_7_v2.mp4'\n"
    )
    
    sftp = ssh.open_sftp()
    remote_list_path = "/root/kaisar_ref_hvatit_platit/concat_final_correct.txt"
    with sftp.file(remote_list_path, "w") as f:
        f.write(concat_list)
        
    print("3. Склеиваем видеоролик на VPS...")
    concat_cmd = (
        "ffmpeg -y -f concat -safe 0 -i /root/kaisar_ref_hvatit_platit/concat_final_correct.txt "
        "-vf 'scale=720:1280,fps=24,format=yuv420p' "
        "-c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k -movflags +faststart "
        "/root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4"
    )
    stdin, stdout, stderr = ssh.exec_command(concat_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при склейке:")
        print(stderr.read().decode("utf-8"))
        sftp.close()
        ssh.close()
        return
        
    print("4. Скачиваем готовый идеальный видеоролик локально...")
    remote_final_video = "/root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4"
    local_final_video = "scratch/kaisar_ref_final_perfect.mp4"
    if os.path.exists(local_final_video):
        os.remove(local_final_video)
    sftp.get(remote_final_video, local_final_video)
    
    sftp.close()
    ssh.close()
    
    print("5. Отправляем идеальный видеоролик в Telegram...")
    bot_token = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
    chat_id = "888005446"
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    caption = (
        "Идеальная версия ролика готова! 🚀\n"
        "- Вернули целую фразу 'И третий - LM арена...' в veo_5.\n"
        "- Полностью удалили лишнюю фразу 'Хочешь понять как использовать ИИ...' из veo_6.\n"
        "- Без зажёванных слов на переходах."
    )
    with open(local_final_video, "rb") as video:
        files = {"video": video}
        data = {"chat_id": chat_id, "caption": caption}
        response = requests.post(url, data=data, files=files)
        
    print("Статус отправки в Telegram:", response.status_code)
    print("Ответ Telegram:", response.text[:500])
    
    if os.path.exists(local_final_video):
        os.remove(local_final_video)
        
if __name__ == "__main__":
    main()
