import os
import sys
import time
import subprocess
import logging
from google import genai
from google.genai import types

# Настройка логирования
log_file = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/night_render.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("Инициализация ночного рендеринга...")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
    logging.info("Клиент Vertex AI успешно инициализирован.")
except Exception as e:
    logging.error(f"Ошибка инициализации Vertex AI: {e}")
    sys.exit(1)

renders_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders"
brain_dir = "/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6"
os.makedirs(renders_dir, exist_ok=True)

edge_tts_path = "/Users/higherpower/Library/Python/3.9/bin/edge-tts"

def generate_tts(text, voice, out_path, rate=None):
    """Генерация аудио через edge-tts с повторными попытками."""
    cmd = [edge_tts_path, "--text", text, "--voice", voice, "--write-media", out_path]
    if rate:
        cmd.extend(["--rate", rate])
    
    for attempt in range(1, 4):
        try:
            logging.info(f"Генерация TTS: {text} (Голос: {voice}, Попытка: {attempt})")
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            logging.info(f"Аудио успешно сохранено: {out_path}")
            return True
        except subprocess.TimeoutExpired as te:
            logging.warning(f"Попытка {attempt} превысила лимит времени (timeout): {te}")
            time.sleep(5)
        except Exception as e:
            logging.warning(f"Попытка {attempt} не удалась: {e}")
            time.sleep(5)
    logging.error(f"Не удалось сгенерировать TTS после 3 попыток: {text}")
    return False

def generate_video_veo(start_image_path, prompt, output_filename, duration=8):
    """Генерация видео через Veo 3.1 (Image-to-Video) с повторными попытками."""
    out_path = os.path.join(renders_dir, output_filename)
    if os.path.exists(out_path):
        logging.info(f"Видео {output_filename} уже существует, пропускаем генерацию.")
        return True

    for attempt in range(1, 4):
        try:
            logging.info(f"Запуск Veo 3.1 для {output_filename} (Попытка {attempt})...")
            with open(start_image_path, "rb") as f:
                start_bytes = f.read()
            start_img = types.Image(image_bytes=start_bytes, mime_type="image/png")

            operation = client.models.generate_videos(
                model="veo-3.1-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    reference_images=[types.VideoGenerationReferenceImage(image=start_img, reference_type="ASSET")],
                    person_generation="ALLOW_ADULT",
                    aspect_ratio="9:16",
                    duration_seconds=duration,
                    generate_audio=False
                )
            )
            
            logging.info(f"Операция Veo создана: {operation.name}. Ожидание завершения...")
            while not operation.done:
                time.sleep(15)
                operation = client.operations.get(operation)
            
            if operation.error:
                logging.warning(f"Ошибка операции Veo: {operation.error}")
                continue
                
            if operation.result and operation.result.generated_videos:
                video_obj = operation.result.generated_videos[0].video
                if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                    with open(out_path, "wb") as f:
                        f.write(video_obj.video_bytes)
                else:
                    import google.cloud.storage as storage
                    storage_client = storage.Client()
                    path_parts = video_obj.uri[5:].split("/", 1)
                    bucket = storage_client.bucket(path_parts[0])
                    bucket.blob(path_parts[1]).download_to_filename(out_path)
                
                logging.info(f"Видео успешно сохранено в {out_path}")
                return True
        except Exception as e:
            logging.error(f"Исключение при генерации Veo: {e}")
            time.sleep(15)
            
    return False

def merge_audio_video(video_path, audio_path, output_path):
    """Склейка видео и аудио через FFmpeg."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", output_path
    ]
    try:
        logging.info(f"Склейка видео {video_path} и аудио {audio_path}...")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logging.info(f"Финальный клип сохранен: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Ошибка склейки FFmpeg: {e}")
        return False

# Спецификация сцен
scenes_config = {
    4: {
        "start_img": os.path.join(brain_dir, "clip4_anime_start.png"),
        "prompt": "2D anime style. A young developer intensely typing and pressing the ENTER key on a mechanical keyboard. Cool blue and green screen glow reflecting on his face. Cinematic camera movement.",
        "silent_video": "clip4_anime_silent.mp4",
        "final_video": os.path.join(renders_dir, "clip4_anime_final.mp4"),
        "tts": [
            {"text": "А ИИ сможет прессовать, как Баке?", "voice": "ru-RU-DmitryNeural", "rate": None},
            {"text": "Еще жестче. Бот готов. Запускаем поток!", "voice": "ru-RU-DmitryNeural", "rate": "+10%"}
        ]
    },
    5: {
        "start_img": os.path.join(brain_dir, "clip5_start_anime.png"),
        "prompt": "2D anime style. Close-up of a smartphone lying on a desk in a dark room. The screen lights up, showing a rapid stream of green popup transaction notifications. Vivid screen glow. Russian text: KASPI ПЕРЕВОД.",
        "silent_video": "clip5_silent.mp4",
        "final_video": os.path.join(renders_dir, "clip5_final.mp4"),
        "tts": [
            {"text": "Смотри, переводы пошли! Пятьдесят тысяч... Сто тысяч!", "voice": "ru-RU-DmitryNeural", "rate": "+5%"}
        ]
    },
    6: {
        "start_img": os.path.join(brain_dir, "clip6_start_hacked.png"),
        "prompt": "2D anime style, dark thriller anime. A laptop screen suddenly turns bright red. The two characters look at it in pure terror. English text: HACKED.",
        "silent_video": "clip6_video_silent.mp4",
        "final_video": os.path.join(renders_dir, "clip6_final.mp4"),
        "tts": [
            {"text": "Мансик! Бот выбил два ляма... Но нас кто-то взломал! Бакой голосом: Бабки уходят на левый криптокошелек!", "voice": "ru-RU-DmitryNeural", "rate": None}
        ]
    },
    7: {
        "start_img": os.path.join(brain_dir, "clip7_start_panic.png"),
        "prompt": "2D anime style, cyberpunk anime. A panicked young developer typing frantically on a mechanical keyboard. Red binary code reflects vividly in his glasses.",
        "silent_video": "clip7_silent.mp4",
        "final_video": os.path.join(renders_dir, "clip7_final.mp4"),
        "tts": [
            {"text": "Если через минуту не остановишь вывод — я с вас шкуру спущу!", "voice": "ru-RU-DmitryNeural", "rate": "+15%"},
            {"text": "Я не могу зайти в админку!", "voice": "ru-RU-DmitryNeural", "rate": "+5%"}
        ]
    },
    8: {
        "start_img": os.path.join(brain_dir, "clip8_start_sparks.png"),
        "prompt": "2D anime style, dramatic anime style. A laptop screen short-circuits with sparks flying, then the screen dies completely. Total darkness.",
        "silent_video": "clip8_silent.mp4",
        "final_video": os.path.join(renders_dir, "clip8_final.mp4"),
        "tts": [
            {"text": "Пароль изменен... Мы потеряли контроль.", "voice": "ru-RU-DmitryNeural", "rate": None}
        ]
    }
}

for scene_id, config in scenes_config.items():
    logging.info(f"=== НАЧАЛО ОБРАБОТКИ СЦЕНЫ {scene_id} ===")
    
    # 1. Генерация видео
    video_ok = generate_video_veo(config["start_img"], config["prompt"], config["silent_video"])
    if not video_ok:
        logging.error(f"Не удалось сгенерировать видео для сцены {scene_id}. Переходим к следующей.")
        continue
        
    # 2. Генерация TTS аудио
    audio_files = []
    for idx, tts_conf in enumerate(config["tts"]):
        audio_name = f"scene{scene_id}_part{idx}.mp3"
        audio_path = os.path.join(renders_dir, audio_name)
        if generate_tts(tts_conf["text"], tts_conf["voice"], audio_path, tts_conf["rate"]):
            audio_files.append(audio_path)
            
    if not audio_files:
        logging.error(f"Нет аудио для сцены {scene_id}. Пропуск склейки.")
        continue
        
    # Склейка аудио частей, если их несколько
    combined_audio = os.path.join(renders_dir, f"scene{scene_id}_combined.mp3")
    if len(audio_files) > 1:
        # Объединяем аудио через ffmpeg concat filter
        cmd = ["ffmpeg", "-y"]
        for f in audio_files:
            cmd.extend(["-i", f])
        filter_str = "".join([f"[{i}:a]" for i in range(len(audio_files))]) + f"concat=n={len(audio_files)}:v=0:a=1[out]"
        cmd.extend(["-filter_complex", filter_str, "-map", "[out]", combined_audio])
        logging.info(f"Объединение аудио для сцены {scene_id}...")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    else:
        combined_audio = audio_files[0]
        
    # 3. Склейка видео и аудио
    merge_audio_video(os.path.join(renders_dir, config["silent_video"]), combined_audio, config["final_video"])

logging.info("Рендеринг всех сцен завершен!")
