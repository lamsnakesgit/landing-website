import os
import json
from pathlib import Path
from core.video_editor import VideoEditor
from core.smart_editor import SmartEditor

def main():
    base_dir = Path(os.getcwd())
    editor = VideoEditor()
    smart = SmartEditor(base_dir)
    
    # 1. Загружаем тайминги от Gemini
    timings_path = base_dir / "outputs" / "word_timings.json"
    if not timings_path.exists():
        print("❌ Тайминги не найдены! Сначала запусти scripts/transcribe_reels.py")
        return
        
    with open(timings_path, "r", encoding="utf-8") as f:
        timings_data = json.load(f)
    
    # 2. Список клипов (отборные дубли)
    clips_dir = base_dir / "outputs" / "clips_v3"
    clips = [
        clips_dir / "scene_1_hook.mp4",
        clips_dir / "scene_2_context.mp4",
        clips_dir / "scene_3_value_fixed.mp4",
        clips_dir / "scene_4_cta_fixed.mp4"
    ]
    
    # 3. Генерируем караоке-оверлеи для каждого клипа
    print("🎨 Генерация динамических караоке-титров...")
    karaoke_data = {}
    for clip_name, words in timings_data.items():
        if words:
            generated_sequence = smart.create_karaoke_sequence(clip_name, words)
            karaoke_data[clip_name] = generated_sequence
            
    # 4. Вотермарк и музыка
    watermark = smart.create_nick_plate("t.me/nnsvt")
    music = base_dir / "assets" / "music" / "background_techno.mp3"
    
    # 5. Итоговый файл
    output = base_dir / "outputs" / "FINAL_REEL_DYNAMIC_V7.mp4"
    
    print("🚀 Запуск финальной динамической сборки (V7)...")
    success = editor.compose_dynamic_insta_reel(
        clips=clips,
        karaoke_data=karaoke_data,
        watermark_path=watermark,
        music_path=music,
        output_path=output,
        speed=1.15 # Ускорение 15%
    )
    
    if success:
        print(f"✨ ШЕДЕВР ГОТОВ! Dynamic V7: {output}")
        print("Это видео ускорено на 15%, голос сохранен, титры - слово за словом.")
    else:
        print("❌ Ошибка при динамическом монтаже.")

if __name__ == "__main__":
    main()
