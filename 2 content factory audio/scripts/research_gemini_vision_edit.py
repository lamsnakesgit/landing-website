import os
import json
from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

def research_multimodal():
    client = genai.Client(api_key=API_KEY)
    
    clips_dir = Path("outputs/clips_v3")
    clip_files = sorted(list(clips_dir.glob("*.mp4")))
    
    print(f"🎬 Загрузка {len(clip_files)} клипов для анализа в Gemini...")
    
    # Подготовка контента для Gemini
    contents = []
    contents.append("Ты — профессиональный AI Director. Твоя задача — отобрать лучшие дубли для рекламного Reels и составить план монтажа.")
    contents.append("Сценарий ролика:")
    contents.append("1. Сцена 1: Хук про увольнения.")
    contents.append("2. Сцена 2: Контекст про замену на нейросети.")
    contents.append("3. Сцена 3: Ценность (ударение должно быть на 'поспевАть').")
    contents.append("4. Сцена 4: CTA (должен быть в женском роде: 'Я подготовила').")
    
    # Загружаем файлы в Gemini File API и ждем их готовности
    parts = []
    import time
    for cf in clip_files:
        print(f"📡 Загрузка {cf.name}...")
        file_ref = client.files.upload(file=cf)
        
        # Ждем пока файл станет ACTIVE
        while file_ref.state.name == "PROCESSING":
            print(f"  ⏳ Файл {cf.name} обрабатывается...")
            time.sleep(2)
            file_ref = client.files.get(name=file_ref.name)
            
        if file_ref.state.name == "FAILED":
            print(f"  ❌ Ошибка обработки файла {cf.name}")
            continue
            
        parts.append(types.Part.from_uri(file_uri=file_ref.uri, mime_type="video/mp4"))
        parts.append(f"Это файл: {cf.name}")

    prompt = """
    Проанализируй прикрепленные видеофайлы и выбери по одному лучшему дублю для каждой из 4-х сцен сценария.
    
    Критерии выбора:
    -scene_3: выбери тот вариант, где ударение в слове 'поспевать' звучит правильно на последний слог.
    -scene_4: выбери тот вариант, где персонаж говорит 'Я подготовила' (женский род).
    -Общее: четкость речи, отсутствие визуальных артефактов (лишнего текста в кадре).
    
    Выдай ответ СТРОГО В ФОРМАТЕ JSON:
    {
      "selected_clips": ["file1.mp4", "file2.mp4", ...],
      "analysis": {
         "file1.mp4": "почему выбрано",
         ...
      },
      "montage_plan": {
         "transition": "fade",
         "duration": 0.5,
         "background_music_vibe": "techno/corporate/serious"
      }
    }
    """
    
    print("🧠 Gemini анализирует видео... (это может занять до минуты)")
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[*parts, prompt],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    
    result = json.loads(response.text)
    print("\n🎯 РЕЗУЛЬТАТ АНАЛИЗА:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    with open("logs/smart_edit_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    research_multimodal()
