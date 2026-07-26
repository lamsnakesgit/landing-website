import os
import sys
import subprocess
import argparse

# Список URL Reels с аккаунта dias_serekbay, полученный в ходе анализа
REELS_URLS = [
    "https://www.instagram.com/reel/DXpJt13jDIv/",
    "https://www.instagram.com/reel/DXVcE7jCLXz/",
    "https://www.instagram.com/reel/DXVa1_WiG98/",
    "https://www.instagram.com/reel/DXCsVPojP_T/",
    "https://www.instagram.com/reel/DW7H78EDOdu/",
    "https://www.instagram.com/reel/DW0pXw_DJk0/",
    "https://www.instagram.com/reel/DUgKHVKjMS-/",
    "https://www.instagram.com/reel/DS74w2fDDIF/",
    "https://www.instagram.com/reel/DQ2GVdLjJY8/",
    "https://www.instagram.com/reel/DHlj8HPiaw1/",
    "https://www.instagram.com/reel/DGQyfCmComn/",
    "https://www.instagram.com/reel/DCExPkEssDG/"
]

def check_and_install_dependencies():
    """Проверяет наличие yt-dlp и устанавливает его при необходимости через pip."""
    try:
        import yt_dlp
        print("yt-dlp уже установлен и доступен для импорта.")
    except ImportError:
        print("yt-dlp не найден. Устанавливаем через pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
            print("yt-dlp успешно установлен.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при установке yt-dlp: {e}")
            sys.exit(1)

def download_video(url, output_dir, browser_name=None):
    """Скачивает одно видео Reels по URL с использованием или без использования cookies браузера."""
    print(f"\nНачало скачивания: {url}")
    # Базовая команда для скачивания с сохранением оригинального названия и ID
    command = [
        sys.executable, "-m", "yt_dlp",
        "-P", output_dir,
        "-o", "%(title)s_%(id)s.%(ext)s",
        url
    ]
    
    # Если указан браузер, подтягиваем cookies для обхода авторизации Instagram
    if browser_name:
        command.extend(["--cookies-from-browser", browser_name])
        
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Успешно скачано: {url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при скачивании {url}: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Скачивание Reels с аккаунта dias_serekbay.")
    parser.add_argument(
        "--browser", 
        type=str, 
        default=None, 
        help="Название браузера для импорта cookies (chrome, safari, edge, firefox, opera)."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="smm_brand_ai/downloaded_reels/dias_serekbay", 
        help="Папка для сохранения скачанных видео."
    )
    args = parser.parse_args()

    # Создаем целевую директорию
    os.makedirs(args.output, exist_ok=True)
    
    # Проверяем зависимости
    check_and_install_dependencies()
    
    success_count = 0
    for idx, url in enumerate(REELS_URLS, 1):
        print(f"\n--- Обработка видео {idx}/{len(REELS_URLS)} ---")
        if download_video(url, args.output, args.browser):
            success_count += 1
            
    print(f"\nСкачивание завершено. Успешно скачано {success_count} из {len(REELS_URLS)} видео.")

if __name__ == "__main__":
    main()
