import os
import sys
import subprocess
import argparse

def check_ffmpeg():
    """Проверяет, установлен ли FFmpeg в системе."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Ошибка: FFmpeg не найден. Установите его через 'brew install ffmpeg' на Mac.")
        return False

def assemble_video(video_path, voice_path, music_path, output_path, music_volume=0.15, fade_duration=1.0):
    """Сводит видео, голос и фоновую музыку в один ролик с помощью FFmpeg.
    
    Применяет авто-приглушение музыки и плавное затухание звука в конце.
    """
    if not os.path.exists(video_path):
        print(f"Ошибка: Видеофайл не найден по пути: {video_path}")
        return False
    if not os.path.exists(voice_path):
        print(f"Ошибка: Файл с голосом не найден по пути: {voice_path}")
        return False

    print("Начало сведения видео и аудио с помощью FFmpeg...")
    
    # Сложный фильтр FFmpeg (filter_complex):
    # 1. Приглушаем фоновую музыку с помощью volume (коэффициент music_volume)
    # 2. Накладываем плавный fade-out (затухание) на музыку в конце
    # 3. Смешиваем (amix) голос и приглушенную музыку в один поток
    # 4. Обрезаем аудио по длительности видео
    
    # Определим длительность видео для применения эффекта затухания (fade-out)
    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    try:
        duration_str = subprocess.check_output(duration_cmd, text=True).strip()
        duration = float(duration_str)
    except Exception:
        # Резервное значение длительности, если ffprobe не смог определить
        duration = 15.0
        
    fade_start = max(0.0, duration - fade_duration)
    
    # Строим команду FFmpeg
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", voice_path
    ]
    
    if music_path and os.path.exists(music_path):
        command.extend(["-i", music_path])
        # Фильтр для смешивания голоса [1:a] и приглушенной музыки [2:a] с fade-out в конце
        filter_str = (
            f"[2:a]volume={music_volume},afade=t=out:st={fade_start}:d={fade_duration}[bg];"
            f"[1:a]afade=t=out:st={fade_start}:d={fade_duration}[voice];"
            f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
    else:
        # Если музыки нет, просто накладываем fade-out на голос
        filter_str = f"[1:a]afade=t=out:st={fade_start}:d={fade_duration}[a]"
        
    command.extend([
        "-filter_complex", filter_str,
        "-map", "0:v",        # Берем видео из первого файла
        "-map", "[a]",        # Берем смешанное аудио из фильтра
        "-c:v", "copy",       # Видео копируем без перекодирования (быстро!)
        "-c:a", "aac",        # Аудио кодируем в AAC
        "-shortest",          # Обрезаем по самому короткому потоку
        output_path
    ])
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Сведение завершено! Готовый ролик сохранен в: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при работе FFmpeg: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Автоматическое сведение ИИ-видео и озвучки с помощью FFmpeg.")
    parser.add_argument("--video", required=True, help="Путь к исходному видео (без звука) из Google Veo.")
    parser.add_argument("--voice", required=True, help="Путь к файлу с голосом (из MiniMax/ElevenLabs).")
    parser.add_argument("--music", default=None, help="Путь к файлу с фоновой музыкой (опционально).")
    parser.add_argument("--output", default="output_reel.mp4", help="Путь к сохранению готового ролика.")
    parser.add_argument("--vol", type=float, default=0.15, help="Громкость фоновой музыки (от 0.0 до 1.0).")
    
    args = parser.parse_args()
    
    if not check_ffmpeg():
        sys.exit(1)
        
    assemble_video(args.video, args.voice, args.music, args.output, args.vol)

if __name__ == "__main__":
    main()
