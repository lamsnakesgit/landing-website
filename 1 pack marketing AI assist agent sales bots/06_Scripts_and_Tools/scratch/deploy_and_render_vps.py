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
    
    # 1. Создаем необходимые папки на VPS
    print("1. Создаем директории на VPS...")
    dirs = [
        "/root/smm_brand_ai/remotion_mvp",
        "/root/smm_brand_ai/remotion_mvp/src",
        "/root/smm_brand_ai/remotion_mvp/src/episode",
        "/root/smm_brand_ai/remotion_mvp/src/hooks",
        "/root/smm_brand_ai/remotion_mvp/public/video"
    ]
    for d in dirs:
        ssh.exec_command(f"mkdir -p {d}")
        
    sftp = ssh.open_sftp()
    
    # 2. Загружаем файлы проекта
    print("2. Загружаем файлы на VPS...")
    local_base = "smm_brand_ai/remotion_mvp"
    remote_base = "/root/smm_brand_ai/remotion_mvp"
    
    files_to_upload = [
        ("package.json", "package.json"),
        ("tsconfig.json", "tsconfig.json"),
        ("src/Root.tsx", "src/Root.tsx"),
        ("src/index.ts", "src/index.ts"),
        ("src/scenes_config.json", "src/scenes_config.json"),
        ("src/hooks/useSceneConfig.ts", "src/hooks/useSceneConfig.ts"),
        ("src/episode/Episode01Perfect.tsx", "src/episode/Episode01Perfect.tsx")
    ]
    
    for local_rel, remote_rel in files_to_upload:
        lpath = os.path.join(local_base, local_rel)
        rpath = os.path.join(remote_base, remote_rel)
        print(f"Загрузка: {lpath} -> {rpath}")
        sftp.put(lpath, rpath)
        
    # 3. Конвертируем MP4 видео разговорного клона в WebM (VP8/Vorbis)
    # ИСПОЛЬЗУЕМ КОРРЕКТНЫЙ kaisar_ref_final_perfect.mp4
    print("3. Конвертируем MP4 разговорного клона в WebM для Chromium (на сервере)...")
    webm_cmd = (
        "ffmpeg -y -i /root/kaisar_ref_hvatit_platit/kaisar_ref_final_perfect.mp4 "
        "-c:v libvpx -crf 10 -b:v 2M -c:a libvorbis "
        "/root/smm_brand_ai/remotion_mvp/public/video/background.webm"
    )
    stdin, stdout, stderr = ssh.exec_command(webm_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при конвертации background в WebM:")
        print(stderr.read().decode("utf-8"))
        sftp.close()
        ssh.close()
        return
        
    # 4. Устанавливаем зависимости и рендерим видео
    print("4. Устанавливаем npm зависимости на VPS...")
    npm_install_cmd = "cd /root/smm_brand_ai/remotion_mvp && npm install"
    stdin, stdout, stderr = ssh.exec_command(npm_install_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при npm install:")
        print(stderr.read().decode("utf-8"))
        sftp.close()
        ssh.close()
        return
        
    print("5. Рендерим видео с помощью Remotion...")
    render_cmd = "cd /root/smm_brand_ai/remotion_mvp && npm run render"
    stdin, stdout, stderr = ssh.exec_command(render_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при рендере Remotion:")
        print(stderr.read().decode("utf-8"))
        sftp.close()
        ssh.close()
        return
        
    print("6. Оптимизируем MP4 для Telegram (Faststart, AAC, H264)...")
    faststart_cmd = (
        "ffmpeg -y -i /root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp.mp4 "
        "-c:v libx264 -preset fast -crf 22 -c:a aac -movflags +faststart "
        "/root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp_faststart.mp4"
    )
    stdin, stdout, stderr = ssh.exec_command(faststart_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print("Ошибка при оптимизации faststart:")
        print(stderr.read().decode("utf-8"))
        sftp.close()
        ssh.close()
        return
        
    print("7. Скачиваем финальный отрендеренный ролик...")
    remote_rendered_video = "/root/smm_brand_ai/remotion_mvp/out/episode_01_remotion_mvp_faststart.mp4"
    local_rendered_video = "scratch/episode_01_remotion_mvp_faststart.mp4"
    if os.path.exists(local_rendered_video):
        os.remove(local_rendered_video)
    sftp.get(remote_rendered_video, local_rendered_video)
    
    sftp.close()
    ssh.close()
    
    print("8. Отправляем отрендеренный ролик в Telegram с корректными метаданными...")
    bot_token = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
    chat_id = "888005446"
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    caption = "Ваш готовый Reels со встроенными B-roll сценами и последовательными субтитрами! 🚀"
    with open(local_rendered_video, "rb") as video:
        files = {"video": video}
        data = {
            "chat_id": chat_id, 
            "caption": caption,
            "width": 720,
            "height": 1280,
            "duration": 49,
            "supports_streaming": True
        }
        response = requests.post(url, data=data, files=files)
        
    print("Статус отправки в Telegram:", response.status_code)
    print("Ответ Telegram:", response.text[:500])
    
    if os.path.exists(local_rendered_video):
        os.remove(local_rendered_video)
        
if __name__ == "__main__":
    main()
