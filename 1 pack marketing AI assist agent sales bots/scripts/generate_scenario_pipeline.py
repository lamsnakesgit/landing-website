import os
import sys
import json
import time
import requests
import subprocess

# Настройки
SA_KEY_PATH = "vertex_sa.json"
if not os.path.exists(SA_KEY_PATH):
    SA_KEY_PATH = "scripts/vertex_sa.json"
if not os.path.exists(SA_KEY_PATH):
    SA_KEY_PATH = "../scripts/vertex_sa.json"
if os.path.exists(SA_KEY_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(SA_KEY_PATH)

PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"
BOT_TOKEN = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
CHAT_ID = "888005446"

# Пул голосов OpenAI: alloy, echo, onyx, nova, shimmer
VOICE = "nova"

def get_api_key(name="OPENAI_API_KEY"):
    env_path = ".env"
    if not os.path.exists(env_path):
        env_path = "../.env"
    if not os.path.exists(env_path):
        env_path = "scripts/.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                # Очищаем лишние кавычки и точки в конце
                if line.startswith(f"{name}="):
                    val = line.strip().split("=")[1].strip()
                    val = val.strip("'\"")
                    if val.endswith('.'):
                        val = val[:-1]
                    return val
    return os.environ.get(name)

# 1. Сценарий от Кайсара (жестко прописанный или извлеченный)
# Разбиваем весь сценарий по фразам/сценам с таймингами (~5-8 секунд)
SCENARIO = [
    {
        "id": 1,
        "text": "90 процентов экспертов сливают весь свой бюджет на рекламу и Reels.",
        "layout": "FULL_SCREEN",
        "duration": 5
    },
    {
        "id": 2,
        "text": "И всё потому, что они совершают одну простую, но фатальную ошибку.",
        "layout": "BOTTOM",
        "duration": 5
    },
    {
        "id": 3,
        "text": "Они не используют ИИ-аватары для автоматического прогрева аудитории.",
        "layout": "B_ROLL",
        "duration": 5
    },
    {
        "id": 4,
        "text": "Вместо этого они часами записывают говорящие головы вручную.",
        "layout": "TOP",
        "duration": 5
    },
    {
        "id": 5,
        "text": "Хочешь узнать, как внедрить авто-генерацию видео и получать лиды на автомате?",
        "layout": "FULL_SCREEN",
        "duration": 5
    },
    {
        "id": 6,
        "text": "Пиши мне слово РОБОТ в личные сообщения, и я пришлю тебе готовый гайд.",
        "layout": "BOTTOM",
        "duration": 5
    }
]

def generate_voice_local(text, output_path, api_key):
    print(f"[*] Генерация озвучки: {text[:30]}...")
    
    # Пытаемся использовать aihubmix если передан, или вычищаем openai_key
    aihub_key = get_api_key("AIHUBMIX_API_KEY")
    if aihub_key:
        api_key = aihub_key
        url = "https://api.aihubmix.com/v1/audio/speech"
    else:
        url = "https://api.openai.com/v1/audio/speech"
        
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "tts-1", "input": text, "voice": VOICE, "response_format": "mp3"}
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(r.content)
            return True
        else:
            print(f"[-] Ошибка TTS (Код {r.status_code}): {r.text}")
    except Exception as e:
        print(f"[-] Исключение TTS: {e}")
    return False

def generate_veo_clip_local(text, voice_path, image_path, output_path):
    print(f"[*] Генерация Veo 3.1 клипа для: '{text[:40]}'")
    from google import genai
    from google.genai import types
    
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        
        # Инструктируем модель оживить лицо под конкретный текст, произносимый на камеру
        prompt_text = f"A photorealistic vertical close-up video of this person speaking directly to the camera. They are naturally speaking, lips and face moving dynamically to pronounce: {text}. High quality, detailed facial features, realistic lip synchronization."
        
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        
        img = types.Image(image_bytes=img_bytes, mime_type="image/png")
        ref_image = types.VideoGenerationReferenceImage(
            image=img,
            reference_type="ASSET"
        )
        
        response = client.models.generate_videos(
            model='veo-3.1-generate-001',
            prompt=prompt_text,
            config=types.GenerateVideosConfig(
                referenceImages=[ref_image],
                aspectRatio="9:16",
                durationSeconds=8
            )
        )
        
        operation = response
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("  ожидание клипа от Veo...")
            
        if operation.error:
            print(f"[-] Ошибка Veo: {operation.error}")
            return False
            
        for gen_video in operation.result.generated_videos:
            temp_silent = output_path + ".silent.mp4"
            with open(temp_silent, "wb") as f:
                f.write(gen_video.video.video_bytes)
            
            # Накладываем сгенерированный голос (voice_path) на видео с помощью FFmpeg
            print(f"[*] Накладываем звук {voice_path} на клип {output_path}...")
            cmd = [
                "ffmpeg", "-y",
                "-i", temp_silent,
                "-i", voice_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                output_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(temp_silent):
                os.remove(temp_silent)
            
            print(f"[+] Клип сгенерирован и озвучен: {output_path}")
            return True
            
    except Exception as e:
        print(f"[-] Исключение Veo: {e}")
    return False

def send_tg_video(video_path, caption):
    print(f"[*] Отправка {video_path} в Telegram...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(video_path, "rb") as f:
            r = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"video": f})
        print(f"[+] Telegram ответ: {r.status_code}")
    except Exception as e:
        print(f"[-] Ошибка отправки в TG: {e}")

def extract_last_frame(video_path, output_image_path):
    print(f"[*] Извлекаем последний кадр из {video_path}...")
    # Команда FFmpeg для извлечения последнего кадра
    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-3", # Ищем в самом конце
        "-i", video_path,
        "-update", "1",
        "-q:v", "1",
        "-frames:v", "1",
        output_image_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"[-] Ошибка извлечения кадра: {e}")
    return False

def main():
    api_key = get_api_key()
    if not api_key:
        print("[-] Ошибка: OPENAI_API_KEY не найден в .env")
        sys.exit(1)
        
    print("=== ЗАПУСК ПОСЛЕДОВАТЕЛЬНОЙ ГЕНЕРАЦИИ SCENARIO ===")
    
    os.makedirs("temp_build", exist_ok=True)
    
    # Стартовое лицо
    current_face_image = "studio_face.png"
    
    for scene in SCENARIO:
        idx = scene["id"]
        text = scene["text"]
        
        voice_path = f"temp_build/voice_{idx}.mp3"
        video_path = f"temp_build/veo_{idx}.mp4"
        
        # Генерируем голос
        if not os.path.exists(voice_path):
            generate_voice_local(text, voice_path, api_key)
            
        # Генерируем Veo клип 9:16 с динамической сменой опорного лица
        if not os.path.exists(video_path):
            print(f"[*] Используем опорное лицо: {current_face_image}")
            success = generate_veo_clip_local(text, voice_path, current_face_image, video_path)
            if success:
                # Отправляем готовую сцену в Telegram пользователю!
                send_tg_video(video_path, f"Сцена {idx} (9:16) сгенерирована!\nТекст: {text}")
                
                # Извлекаем последний кадр для следующей сцены
                next_face = f"temp_build/face_after_{idx}.png"
                if extract_last_frame(video_path, next_face):
                    current_face_image = next_face
            else:
                print(f"[-] Не удалось сгенерировать клип {idx}")
        else:
            print(f"[+] Клип {idx} уже существует. Пропускаем.")
            send_tg_video(video_path, f"Сцена {idx} (из кэша):\nТекст: {text}")
            
            # Если берем из кэша, всё равно обновляем текущее лицо
            next_face = f"temp_build/face_after_{idx}.png"
            if os.path.exists(next_face):
                current_face_image = next_face
            elif os.path.exists(video_path):
                if extract_last_frame(video_path, next_face):
                    current_face_image = next_face

if __name__ == "__main__":
    main()
