import os
from pathlib import Path
from core.video_editor import VideoEditor

def finalize():
    base_dir = Path(__file__).parent.parent
    clips_dir = base_dir / "outputs" / "clips"
    output_path = base_dir / "outputs" / "story_fired_programmers_final.mp4"
    
    # Собираем клипы в правильном порядке
    scene_ids = ["scene_1_hook", "scene_2_context", "scene_3_value", "scene_4_cta"]
    clip_paths = []
    
    for sid in scene_ids:
        p = clips_dir / f"{sid}.mp4"
        if p.exists():
            clip_paths.append(p)
        else:
            print(f"⚠️ Пропуск: Клип {sid} не найден.")
            
    if len(clip_paths) == 0:
        print("❌ Нечего склеивать.")
        return

    editor = VideoEditor(ffmpeg_path="/opt/homebrew/bin/ffmpeg")
    
    # Шаг 1: Склейка
    success = editor.concatenate_clips(clip_paths, output_path)
    
    if success:
        print(f"🎉 ФИНАЛЬНЫЙ РОЛИК ГОТОВ: {output_path}")
        
        # Шаг 2: Можно добавить музыку если она есть
        # editor.add_background_music(output_path, "assets/music/business_dynamic.mp3", output_path)
    else:
        print("❌ Ошибка при создании финального ролика.")

if __name__ == "__main__":
    finalize()
