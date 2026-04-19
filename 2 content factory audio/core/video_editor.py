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

    def compose_dynamic_insta_reel(self, clips, karaoke_data, watermark_path, music_path, output_path, speed=1.15):
        """
        Финальный монтаж в стиле Insta/Hormozi:
        - Склейка
        - Ускорение (1.15x)
        - Динамические титры по таймингу
        - Музыка
        """
        # 1. Склеиваем клипы
        temp_concat = "outputs/temp/temp_concat.mp4"
        if not self.concatenate_clips(clips, temp_concat):
            return False
            
        print(f"⚡️ Применение ускорения {speed}x и наложение титров...")
        
        # Строим фильтры для титров
        # Мы должны учитывать, что склеенное видео длинное, а тайминги в данных - для каждого клипа отдельно.
        # Поэтому нам нужно высчитать смещение для каждой сцены (8 сек на сцену)
        
        filter_parts = []
        input_index = 2 # 0: video, 1: watermark, 2+: words
        
        # Базовое ускорение видео
        # Сначала ускоряем основной поток видео, чтобы губы совпадали с ускоренным звуком
        filter_parts.append(f"[0:v]setpts=PTS/{speed}[v_fast]")
        overlay_chain = "[v_fast]"
        
        # Сцены идут по 8 сек. С учетом xfade (0.5с), каждая следующая сцена начинается на 7.5с позже.
        scene_offsets = [0.0, 7.5, 15.0, 22.5]
        
        inputs = [self.ffmpeg_path, "-y", "-i", temp_concat, "-i", str(watermark_path)]
        
        for scene_idx, (clip_name, words) in enumerate(karaoke_data.items()):
            offset = scene_offsets[scene_idx]
            for word_data in words:
                word_path = word_data["path"]
                # Пересчитываем время с учетом ускорения
                start = (offset + word_data["start"]) / speed
                end = (offset + word_data["end"]) / speed
                
                inputs.extend(["-i", str(word_path)])
                next_chain = f"[v{input_index}]"
                filter_parts.append(f"{overlay_chain}[{input_index}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{next_chain}")
                overlay_chain = next_chain
                input_index += 1
                
        # Добавляем вотермарк в конце цепочки
        final_v_chain = f"{overlay_chain}[1:v]overlay=0:0[v_branded]"
        filter_parts.append(final_v_chain)
        
        # Ускорение и микс аудио
        # Сначала ускоряем оригинал, потом миксуем с музыкой
        # Индекс музыки - это последний добавленный вход (input_index)
        music_input_idx = input_index 
        audio_filter = f"[0:a]atempo={speed}[a_fast]; [{music_input_idx}:a]volume=0.1[bg]; [a_fast][bg]amix=inputs=2:duration=first[aout]"
        inputs.extend(["-i", str(music_path)]) # Музыка будет последним вводом
        
        # Собираем всё в один запуск
        full_filter = "; ".join(filter_parts) + f"; {audio_filter}"
        
        cmd = inputs + [
            "-filter_complex", full_filter,
            "-map", "[v_branded]", "-map", "[aout]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ]
        
        print(f"🎬 Рендеринг финального ролика (всего слоев: {input_index})...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка рендеринга: {result.stderr}")
        return result.returncode == 0
