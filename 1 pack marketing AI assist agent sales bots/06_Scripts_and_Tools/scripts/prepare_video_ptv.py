import subprocess
import os
import sys

def prepare_video_for_ptv(input_file, output_file=None):
    """
    Превращает любое видео в квадратный формат 1:1 для WhatsApp Video Notes (кружочков).
    Использует FFmpeg для центрированного кроппинга и масштабирования.
    """
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_ptv.mp4"

    # Команда FFmpeg:
    # 1. crop=min(iw,ih):min(iw,ih) - делает квадрат по меньшей стороне
    # 2. scale=640:640 - стандартное разрешение для кружочков
    # 3. Настройки кодека для максимальной совместимости с мобилками
    
    command = [
        "ffmpeg", "-i", input_file,
        "-vf", "crop=min(iw\,ih):min(iw\,ih),scale=640:640",
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-y",
        output_file
    ]

    try:
        print(f"Обработка видео: {input_file} -> {output_file}")
        subprocess.run(command, check=True, capture_output=True)
        print("Успешно завершено!")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обработке: {e.stderr.decode()}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python prepare_video_ptv.py <input_video>")
    else:
        prepare_video_for_ptv(sys.argv[1])
