import os
from pathlib import Path
from core.video_editor import VideoEditor

def main():
    base_dir = Path(os.getcwd())
    editor = VideoEditor()
    
    # 1. Выбираем лучшие дубли (согласно анализу Gemini)
    clips_dir = base_dir / "outputs" / "clips_v3"
    clips = [
        clips_dir / "scene_1_hook.mp4",
        clips_dir / "scene_2_context.mp4",
        clips_dir / "scene_3_value_fixed.mp4",
        clips_dir / "scene_4_cta_fixed.mp4"
    ]
    
    # 2. Оверлеи (Premium Стиль)
    overlay_dir = base_dir / "outputs" / "overlays"
    from core.smart_editor import SmartEditor
    smart = SmartEditor(base_dir)
    
    print("🎨 Генерация премиум-графики...")
    overlays = [
        smart.create_text_overlay("Вчера уволили 20% программистов топовой компании. И дело не в кризисе.", "p_scene_1.png"),
        smart.create_text_overlay("Их заменили на тех, кто вовремя перешёл на нейросети. Время ханжей и зануд прошло.", "p_scene_2.png"),
        smart.create_text_overlay("Технологии заменяют тех, кто перестал за ними поспевать. Либо ты настраиваешь систему, либо она выбрасывает тебя.", "p_scene_3.png"),
        smart.create_text_overlay("Я подготовила гайд, как запустить автономного агента 24/7. Пиши кодовое слово АГЕНТ в директ.", "p_scene_4.png")
    ]
    watermark = smart.create_nick_plate("t.me/nnsvt")
    
    # 3. Музыка
    music = base_dir / "assets" / "music" / "background_techno.mp3"
    
    # 4. Выходной файл
    output = base_dir / "outputs" / "FINAL_REEL_PREMIUM_v1.mp4"
    
    print("🚀 Запуск финальной PREMIUM сборки Smart Montage...")
    success = editor.compose_final_reel(
        clip_paths=clips,
        overlay_paths=overlays,
        watermark_path=watermark,
        music_path=music,
        output_path=output
    )
    
    if success:
        print(f"✨ ШЕДЕВР ГОТОВ! Premium v1: {output}")
    else:
        print("❌ Ошибка при монтаже.")

if __name__ == "__main__":
    main()
