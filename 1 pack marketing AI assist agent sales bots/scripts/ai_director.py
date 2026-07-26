import os
import sys
import json
import requests
import subprocess
import argparse

def get_api_key():
    """Считывает OPENAI_API_KEY из файла .env."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
    return os.environ.get("OPENAI_API_KEY")

def generate_script(topic, api_key):
    """Генерирует сценарий из 3 сцен по формуле удержания через GPT-4o-mini."""
    print("Генерация сценария через GPT-4o-mini...")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = (
        f"Создай сценарий для Reels на 15 секунд на тему: '{topic}'. "
        f"Раздели на 3 сцены по 5 секунд. "
        f"Для каждой сцены дай JSON: "
        f"1. 'voice_text' (реплика для озвучки на русском, 1-2 предложения), "
        f"2. 'image_prompt' (детальный промпт для DALL-E 3 на английском, в стиле 3D Pixar, яркие цвета), "
        f"3. 'voice_actor' (alloy, echo, или onyx для мужских сцен, nova или shimmer для женских). "
        f"Ответь строго в формате JSON списка объектов."
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        # Парсим JSON
        data = json.loads(content)
        return data.get("scenes", data.get("list", list(data.values())[0]))
    except Exception as e:
        print(f"Ошибка при генерации сценария: {e}")
        return None

def generate_image(prompt, output_path, api_key):
    """Генерирует вертикальное изображение 9:16 через DALL-E 3."""
    print(f"Генерация кадра DALL-E 3 по промпту: {prompt[:50]}...")
    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {
        "model": "dall-e-3",
        "prompt": f"{prompt}, 3d pixar style, vibrant colors, detailed, portrait orientation",
        "n": 1,
        "size": "1024x1792", # Формат 9:16
        "quality": "standard"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        img_url = result["data"][0]["url"]
        # Скачиваем картинку
        img_data = requests.get(img_url).content
        with open(output_path, "wb") as f:
            f.write(img_data)
        return True
    except Exception as e:
        print(f"Ошибка генерации картинки: {e}")
        return False

def generate_voice(text, voice, output_path, api_key):
    """Генерирует озвучку через OpenAI TTS."""
    print(f"Генерация озвучки: '{text[:30]}...' (Голос: {voice})")
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "tts-1", "input": text, "voice": voice, "response_format": "mp3"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Ошибка генерации голоса: {e}")
        return False

def create_scene_video(image_path, audio_path, output_path):
    """Создает видеоклип из статичной картинки и аудиодорожки с помощью FFmpeg."""
    print(f"Сборка клипа сцены: {output_path}...")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка FFmpeg при сборке сцены: {e.stderr.decode()}")
        return False

def concatenate_scenes(scene_files, music_path, output_path):
    """Объединяет все сцены и накладывает фоновую музыку."""
    print("Финальное склеивание всех сцен и наложение музыки...")
    # Создаем файл списка для склейки
    list_path = "temp_scenes.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for file in scene_files:
            f.write(f"file '{file}'\n")
            
    # Временный склеенный файл без музыки
    temp_concat = "temp_concat.mp4"
    concat_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", temp_concat]
    
    try:
        subprocess.run(concat_cmd, check=True, capture_output=True)
        
        # Накладываем музыку на склеенное видео
        # Вызываем наш готовый assemble_video.py
        assemble_script = os.path.join(os.path.dirname(__file__), "assemble_video.py")
        # Для извлечения звука из склеенного видео создаем временную аудиодорожку
        temp_audio = "temp_voice.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", temp_concat, "-q:a", "0", "-map", "a", temp_audio], check=True, capture_output=True)
        
        # Запускаем assemble_video
        scripts_dir = os.path.dirname(__file__)
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        from assemble_video import assemble_video as run_assemble
        run_assemble(temp_concat, temp_audio, music_path, output_path)
        
        # Удаляем временные файлы
        for f in [list_path, temp_concat, temp_audio] + scene_files:
            if os.path.exists(f):
                os.remove(f)
        return True
    except Exception as e:
        print(f"Ошибка сборки финального видео: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ИИ-Режиссер: Генерация Reels под ключ.")
    parser.add_argument("--topic", required=True, help="Тема для генерации видеоролика.")
    parser.add_argument("--music", default=None, help="Путь к файлу фоновой музыки.")
    parser.add_argument("--output", default="final_reel.mp4", help="Имя итогового видеофайла.")
    args = parser.parse_args()
    
    api_key = get_api_key()
    if not api_key:
        print("Ошибка: OPENAI_API_KEY не найден в .env")
        sys.exit(1)
        
    scenes = generate_script(args.topic, api_key)
    if not scenes:
        sys.exit(1)
        
    print(f"Сгенерирован сценарий из {len(scenes)} сцен. Начинаем рендеринг медиа...")
    
    scene_files = []
    for idx, scene in enumerate(scenes, 1):
        img_file = f"temp_img_{idx}.png"
        aud_file = f"temp_aud_{idx}.mp3"
        vid_file = f"temp_vid_{idx}.mp4"
        
        # Генерируем изображение
        if not generate_image(scene["image_prompt"], img_file, api_key):
            continue
        # Генерируем озвучку
        if not generate_voice(scene["voice_text"], scene["voice_actor"], aud_file, api_key):
            continue
        # Создаем видеоклип сцены
        if create_scene_video(img_file, aud_file, vid_file):
            scene_files.append(vid_file)
            
        # Удаляем временные изображения и аудио
        for f in [img_file, aud_file]:
            if os.path.exists(f):
                os.remove(f)
                
    if scene_files:
        concatenate_scenes(scene_files, args.music, args.output)
        print("\n=== Процесс завершен! Видео готово к публикации! ===")
    else:
        print("Ошибка: Не удалось сгенерировать сцены.")

if __name__ == "__main__":
    main()
