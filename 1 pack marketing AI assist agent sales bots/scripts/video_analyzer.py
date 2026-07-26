import os
import json
import subprocess
from scenedetect import detect, ContentDetector
import whisper

def download_video(url, output_path="temp_video.mp4"):
    print(f"[*] Скачивание видео с {url}...")
    cmd = [
        "python3", "-m", "yt_dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", output_path,
        url
    ]
    subprocess.run(cmd, check=True)
    return output_path

def analyze_scenes(video_path):
    print("[*] Анализ динамики монтажа (поиск склеек)...")
    # Используем ContentDetector для поиска резких смен кадра (cuts)
    scene_list = detect(video_path, ContentDetector())
    scenes = []
    for i, scene in enumerate(scene_list):
        scenes.append({
            "scene": i + 1,
            "start_time": scene[0].get_seconds(),
            "end_time": scene[1].get_seconds(),
            "duration": scene[1].get_seconds() - scene[0].get_seconds()
        })
    return scenes

def transcribe_audio(video_path):
    print("[*] Транскрибация текста (вытаскиваем хуки и сценарий)...")
    # Загружаем модель whisper (base - легкая модель)
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    return segments, result["text"]

def main():
    import sys
    if len(sys.argv) < 2:
        print("Использование: python video_analyzer.py <URL>")
        sys.exit(1)
        
    url = sys.argv[1]
    video_path = "temp_video.mp4"
    
    try:
        if os.path.exists(url) and not url.startswith("http"):
            video_path = url
            print(f"[*] Используем локальный файл: {video_path}")
        else:
            if os.path.exists(video_path):
                os.remove(video_path)
            download_video(url, video_path)
        
        # 1. Анализируем монтаж (смены сцен)
        scenes = analyze_scenes(video_path)
        
        # 2. Транскрибируем звук
        text_segments, full_text = transcribe_audio(video_path)
        
        # Формируем итоговый JSON
        output = {
            "source_url": url,
            "full_script": full_text,
            "editing_dynamics": scenes,
            "script_timeline": text_segments
        }
        
        with open("analysis_result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print("\n[+] Готово! Результат сохранен в analysis_result.json")
        print(f"[+] Найдено сцен (склеек): {len(scenes)}")
        print(f"[+] Текст: {full_text[:100]}...")
        
    except Exception as e:
        print(f"[!] Ошибка: {e}")

if __name__ == "__main__":
    main()
