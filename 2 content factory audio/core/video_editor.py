import os
import subprocess
from pathlib import Path

class VideoEditor:
    """
    Класс для автоматического монтажа видео клипов с использованием FFmpeg.
    Поддерживает плавные переходы (xfade).
    """
    def __init__(self, ffmpeg_path="/opt/homebrew/bin/ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        if not Path(ffmpeg_path).exists():
            self.ffmpeg_path = "ffmpeg"

    def concatenate_clips(self, clip_paths, output_path, transition_duration=0.5):
        """
        Склеивает список клипов в один файл с использованием плавных переходов (xfade).
        transition_duration - длительность перехода в секундах.
        """
        if not clip_paths:
            print("❌ Нет клипов для склейки.")
            return False

        if len(clip_paths) < 2:
            cmd = [self.ffmpeg_path, "-y", "-i", str(clip_paths[0]), "-c", "copy", str(output_path)]
            subprocess.run(cmd, check=True)
            return True

        # Для xfade нам нужно строить сложный фильтр. 
        # Допустим каждый клип по 8 сек.
        # offset1 = 8 - 0.5 = 7.5
        # offset2 = 7.5 + 8 - 0.5 = 15
        
        # Динамический расчет офсетов
        input_args = []
        filter_complex = ""
        last_v_label = "[0:v]"
        last_a_label = "[0:a]"
        
        current_offset = 8.0 # Базовая длительность клипа Veo (у нас 8 сек)
        # В идеале нужно мерить ffprobe-ом каждый клип, но для Veo 8s это константа.

        for i in range(1, len(clip_paths)):
            offset = (i * current_offset) - (i * transition_duration)
            
            # Видео переход
            v_out = f"v{i}"
            filter_complex += f"{last_v_label}[{i}:v]xfade=transition=fade:duration={transition_duration}:offset={offset}[{v_out}];"
            last_v_label = f"[{v_out}]"
            
            # Аудио переход (амакс для плавности звука)
            a_out = f"a{i}"
            filter_complex += f"{last_a_label}[{i}:a]acrossfade=d={transition_duration}[{a_out}];"
            last_a_label = f"[{a_out}]"

        cmd = [self.ffmpeg_path, "-y"]
        for p in clip_paths:
            cmd.extend(["-i", str(p)])
        
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", last_v_label, "-map", last_a_label,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ])
        
        print(f"🎬 Запуск профессионального монтажа с xfade ({len(clip_paths)} клипов)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Монтаж завершен: {output_path}")
            return True
        else:
            print(f"❌ Ошибка FFmpeg: {result.stderr}")
            return False

    def add_background_music(self, video_path, music_path, output_path, music_volume=0.15):
        """
        Накладывает фоновую музыку.
        """
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", str(video_path),
            "-i", str(music_path),
            "-filter_complex", f"[1:a]volume={music_volume}[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
