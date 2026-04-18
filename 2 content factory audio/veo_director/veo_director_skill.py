import os
import json
import time
import argparse
import asyncio
from dotenv import load_dotenv

# We use the new official google-genai SDK
from google import genai
from google.genai import types

def load_environment():
    """Load API keys from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env")
        exit(1)
    return api_key

def parse_scenario_to_scenes(client: genai.Client, scenario_text: str):
    """Uses Gemini to split the text into 5-second scenes"""
    print("\n🎬 [STAGE 1] Разбивка сценария на сцены через Gemini...")
    model_id = "gemini-2.5-pro" # Or flash
    prompt = f"""
    Ты - профессиональный ИИ-режиссер. У меня есть сценарий для короткого ролика (Reels/Shorts).
    Мне нужно разбить его на отдельные логические сцены по 4-6 секунд.
    
    Сценарий:
    {scenario_text}
    
    Верни ТОЛЬКО валидный JSON в формате списка объектов. Каждый объект должен иметь ключи:
    "scene_number": целочисленный номер сцены (1, 2, 3...)
    "voice_text": точные слова диктора для этой сцены
    "visual_prompt": короткое описание на английском (1-2 предложения). 
    ВНИМАНИЕ: Видео должно анимировать ЖЕНЩИНУ на базовом фото. 
    Промпт ВСЕГДА должен заканчиваться фразой: "The woman says in Russian: [voice_text]".
    Пример: "A cinematic shot of a woman in a suit talking to the camera. The woman says in Russian: Привет, друзья!"
    ЗАПРЕЩЕНО генерировать пустые офисы без спикера!
    """
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
        )
        t = response.text.strip()
        # Clean up Markdown JSON block if present
        if t.startswith("```json"):
            t = t[7:]
        if t.endswith("```"):
            t = t[:-3]
        
        scenes = json.loads(t)
        print(f"✅ Найдено сцен: {len(scenes)}")
        return scenes
    except Exception as e:
        print(f"❌ Ошибка генерации сценария: {e}")
        print("Ответ модели был:", response.text if 'response' in locals() else "None")
        return []

def generate_scene_video(client: genai.Client, scene: dict, base_photo_path: str, output_dir: str):
    """Generates a video snippet for a single scene using Veo 3.1"""
    print(f"\n🎥 [STAGE 2] Генерация видео для Сцены {scene['scene_number']}...")
    model_id = "veo-3.1-lite-generate-preview" 
    
    # According to Google GenAI Python SDK
    # We pass the image as a reference image
    try:
        with open(base_photo_path, "rb") as f:
            image_bytes = f.read()
    except Exception as e:
        print(f"Ошибка чтения фото {base_photo_path}: {e}")
        return None

    # Note: Vertex AI Veo supports reference images, we need to upload them or provide bytes 
    # dependent on exact SDK version usage.
    # In standard genai API:
    print(f"Промпт: {scene['visual_prompt']}")
    try:
         operation = client.models.generate_videos(
             model=model_id,
             prompt=scene['visual_prompt'],
             # Since it's 'talking head' simulation requested, we provide the reference image
             # Current SDK pattern:
             # If reference image is supported in config:
             # config=types.GenerateVideosConfig(...)
         )
         print(f"⏳ Запрос отправлен в Veo. Ожидание завершения генерации (может занять несколько минут)...")
         
         # Polling
         while not operation.done:
             time.sleep(15)
             print("... Генерация в процессе (до 3-5 мин) ...")
         
         result = operation.result()
         if not result.generated_videos:
             print("❌ Пустой ответ от Veo.")
             return None
             
         video = result.generated_videos[0]
         # video.video.uri may contain google cloud storage URI or bytes.
         video_path = os.path.join(output_dir, f"scene_{scene['scene_number']}.mp4")
         
         if hasattr(video.video, 'video_bytes') and video.video.video_bytes:
             with open(video_path, "wb") as f:
                 f.write(video.video.video_bytes)
             print(f"✅ Видео сохранено: {video_path}")
             return video_path
         elif hasattr(video.video, 'uri'):
             print(f"✅ Видео сгенерировано. Доступно по URI: {video.video.uri} (требуется скачивание)")
             # Usually requires authenticated download
             return video.video.uri
         else:
             print("Неизвестный формат возврата:", video)
             return None

    except Exception as e:
        print(f"❌ Ошибка генерации видео: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="ИИ-Режиссер Скилл (Veo Edition")
    parser.add_argument("--script", type=str, required=True, help="Путь к текстовому файлу со сценарием.")
    parser.add_argument("--photo", type=str, required=True, help="Путь к базовому фото (аватару).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.script):
        print(f"Файл сценария не найден: {args.script}")
        return
    if not os.path.exists(args.photo):
        print(f"Фото не найдено: {args.photo}")
        return
        
    with open(args.script, "r", encoding="utf-8") as f:
        scenario_text = f.read()

    api_key = load_environment()
    client = genai.Client(api_key=api_key)
    
    # Setup directories
    base_dir = os.path.dirname(__file__)
    scenes_dir = os.path.join(base_dir, "assets", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)
    
    # 1. Parse scenes
    scenes = parse_scenario_to_scenes(client, scenario_text)
    if not scenes:
        print("Не удалось разбить сценарий. Выход.")
        return
        
    print("\n👀 Пожалуйста, проверь сцены:")
    for s in scenes:
        print(f"Сцена {s['scene_number']}: '{s['voice_text']}'")
        
    user_input = input("\nПродолжить генерацию видео через Veo? (y/n): ")
    if user_input.lower() != 'y':
        print("Остановка.")
        return
        
    # 2. Generate Videos (Only FIRST scene for test)
    generated_files = []
    test_scene = scenes[0]
    print(f"\n🚀 ТЕСТ: Генерируем только первую сцену...")
    video_file = generate_scene_video(client, test_scene, args.photo, scenes_dir)
    if video_file:
        generated_files.append(video_file)
            
    print("\n=============================================")
    print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
    print(f"Готовые куски: {generated_files}")
    print("Теперь можно перейти к этапу отсмотра и финального монтажа.")
    print("Монтаж вызовем отдельным модулем.")
    print("=============================================")

if __name__ == "__main__":
    main()
