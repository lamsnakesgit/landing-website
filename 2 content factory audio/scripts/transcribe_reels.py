import os
import json
import time
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv()

def transcribe_clips():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ОШИБКА: GOOGLE_API_KEY не найден. Проверь файл .env.")
        return
    
    client = genai.Client(api_key=api_key)
    clips_dir = Path("outputs/clips_v3")
    output_file = Path("outputs/word_timings.json")
    
    # Файлы, которые нам нужны
    selected_clips = [
        "scene_1_hook.mp4",
        "scene_2_context.mp4",
        "scene_3_value_fixed.mp4",
        "scene_4_cta_fixed.mp4"
    ]
    
    all_timings = {}
    
    for clip_name in selected_clips:
        clip_path = clips_dir / clip_name
        if not clip_path.exists():
            print(f"⚠️ Файл {clip_name} не найден, пропускаю.")
            continue
            
        print(f"📡 Загружаем {clip_name} для транскрибации...")
        file_ref = client.files.upload(file=clip_path)
        
        # Ждем обработки
        while file_ref.state.name == "PROCESSING":
            time.sleep(2)
            file_ref = client.files.get(name=file_ref.name)
            
        print(f"🕵️‍♂️ Анализируем тайминги для {clip_name}...")
        prompt = (
            "Watch this 8-second video. Transcribe the speech EXACTLY and provide word-level timestamps "
            "in valid JSON format: { \"words\": [ {\"word\": \"слово\", \"start\": 0.1, \"end\": 0.5}, ... ] }. "
            "Ensure 'start' and 'end' are in seconds. Respond ONLY with JSON."
        )
        
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[file_ref, prompt],
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        try:
            # Очистка от markdown ```json
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            all_timings[clip_name] = json.loads(clean_json)["words"]
            print(f"✅ Тайминги для {clip_name} получены.")
        except Exception as e:
            print(f"❌ Ошибка парсинга для {clip_name}: {e}")
            all_timings[clip_name] = []
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_timings, f, ensure_ascii=False, indent=2)
    print(f"✨ Все тайминги сохранены в {output_file}")

if __name__ == "__main__":
    transcribe_clips()
