import telebot
import sys
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import requests
import json
from datetime import datetime

# Конфигурация
BOT_TOKEN = "8244740843:AAGMVXaIBOu0Mym0DOcilwcElzjlBjY-xwU"
NOTIFICATION_BOT_TOKEN = "8764670738:AAFhAWUVxuCPEnz543glh0euEUvI0UqkbZU"
NOTIFY_CHAT_ID = "888005446"
ALLOWED_USERS = ["mesmerou", "nnsvt"]

PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"
VOICE = "nova"

bot = telebot.TeleBot(BOT_TOKEN)

# Структура сценария (Скрипт Кайсара про бесплатные ИИ-сервисы)
SCENARIO = [
    {"id": 1, "text": "Хватит платить за дорогие ИИ-инструменты! Эти три сайта позволяют создавать качественный ИИ-контент полностью бесплатно."},
    {"id": 2, "text": "Первый — QWEN. Он генерирует и изображение, и видео. Да, он немного медленнее, но качество удивительно хорошее."},
    {"id": 3, "text": "Второй — HUNYUAN. Он с открытым исходным кодом и позволяет создавать кинематографичные визуалы просто из запросов."},
    {"id": 4, "text": "Плюс он поддерживает мощные модели типа LTX и другие современные видео-генераторы."},
    {"id": 5, "text": "И третий — LM Arena. Здесь ты можешь сравнивать несколько ИИ-моделей бок о бок и мгновенно видеть разные результаты."},
    {"id": 6, "text": "Так что вместо угадывания ты точно знаешь, какой инструмент использовать. Хочешь понять, как использовать ИИ каждый день? Пиши мне слово ИИ в личные сообщения."}
]

# Хранилище сессий
# session = { "current_step": 1, "face_image": "studio_face.png" }
SESSION_FILE = "temp_build/session.json"

def get_api_key(name="OPENAI_API_KEY"):
    env_path = ".env"
    if not os.path.exists(env_path):
        env_path = "../.env"
    if not os.path.exists(env_path):
        env_path = "scripts/.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{name}="):
                    val = line.strip().split("=")[1].strip().strip("'\"")
                    if val.endswith('.'): val = val[:-1]
                    return val
    return os.environ.get(name)

def load_session():
    os.makedirs("temp_build", exist_ok=True)
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {"current_step": 1, "face_image": "studio_face.png"}

def save_session(session):
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)

def send_notification(username, text, message_type="сообщение"):
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"👤 Попытка доступа!\n📅 Время: {time_str}\n🔗 Юзернейм: @{username}\nТип: {message_type}\n📝 Действие: {text}"
    url = f"https://api.telegram.org/bot{NOTIFICATION_BOT_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": NOTIFY_CHAT_ID, "text": log_msg})
    except Exception as e: print(e)

def check_access(message):
    username = message.from_user.username
    if username and username.lower() in [u.lower() for u in ALLOWED_USERS]:
        return True
    promo = (
        "Приветствую! 🤖 Этот ИИ-ассистент настроен под приватные задачи владельца, и его личные данные защищены.\n\n"
        "Мы создаем и внедряем умных ИИ-агентов для компаний с отделами продаж от 5–10 человек, а также автоматизируем работу с трафиком, упаковкой и контентным прогревом. Пишите создателю напрямую: @nnsvt 🚀"
    )
    bot.send_message(message.chat.id, promo)
    send_notification(username, message.text if message.text else "[Медиа]", "попытка входа")
    return False

def generate_voice_local(text, output_path):
    api_key = get_api_key("AIHUBMIX_API_KEY") or get_api_key("OPENAI_API_KEY")
    url = "https://api.aihubmix.com/v1/audio/speech" if get_api_key("AIHUBMIX_API_KEY") else "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "tts-1", "input": text, "voice": VOICE, "response_format": "mp3"}
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        with open(output_path, "wb") as f: f.write(r.content)
        return True
    return False

def generate_veo_clip_local(text, voice_path, image_path, output_path):
    from google import genai
    from google.genai import types
    
    sa_path = "vertex_sa.json"
    if not os.path.exists(sa_path): sa_path = "scripts/vertex_sa.json"
    if not os.path.exists(sa_path): sa_path = "../scripts/vertex_sa.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(sa_path)
    
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        prompt_text = f"A photorealistic vertical close-up video of this person speaking directly to the camera. They are naturally speaking, lips and face moving dynamically to pronounce: {text}. High quality, detailed facial features, realistic lip synchronization."
        
        with open(image_path, "rb") as f: img_bytes = f.read()
        img = types.Image(image_bytes=img_bytes, mime_type="image/png")
        ref_image = types.VideoGenerationReferenceImage(image=img, reference_type="ASSET")
        
        response = client.models.generate_videos(
            model='veo-3.1-generate-001',
            prompt=prompt_text,
            config=types.GenerateVideosConfig(referenceImages=[ref_image], aspectRatio="9:16", durationSeconds=8)
        )
        
        operation = response
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            
        for gen_video in operation.result.generated_videos:
            temp_silent = output_path + ".silent.mp4"
            with open(temp_silent, "wb") as f: f.write(gen_video.video.video_bytes)
            
            # Склеиваем с голосом
            cmd = ["ffmpeg", "-y", "-i", temp_silent, "-i", voice_path, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", output_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(temp_silent): os.remove(temp_silent)
            return True
    except Exception as e:
        print(f"[-] Исключение Veo: {e}")
    return False

def extract_last_frame(video_path, output_image_path):
    cmd = ["ffmpeg", "-y", "-sseof", "-3", "-i", video_path, "-update", "1", "-q:v", "1", "-frames:v", "1", output_image_path]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except: return False

@bot.message_handler(commands=['start', 'run_pipeline'])
def start_pipeline(message):
    if not check_access(message): return
    
    session = load_session()
    step = session["current_step"]
    
    if step > len(SCENARIO):
        bot.reply_to(message, "🎉 Все сцены сгенерированы! Для сброса введите /reset")
        return
        
    scene = SCENARIO[step - 1]
    bot.send_message(message.chat.id, f"🎬 **Запуск генерации Сцены {step}/{len(SCENARIO)}**\nТекст: {scene['text']}")
    
    voice_path = f"temp_build/voice_{step}.mp3"
    video_path = f"temp_build/veo_{step}.mp4"
    
    # 1. Генерируем голос
    generate_voice_local(scene["text"], voice_path)
    
    # 2. Генерируем клип
    bot.send_message(message.chat.id, "⏳ Рендеринг клипа Veo 3.1 Lite (8 сек)...")
    success = generate_veo_clip_local(scene["text"], voice_path, session["face_image"], video_path)
    
    if success:
        # Отправляем клип на апрув
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Апрув и получить лицо", callback_data="approve_step"),
            InlineKeyboardButton("❌ Перегенерировать", callback_data="redo_step")
        )
        with open(video_path, "rb") as f:
            bot.send_video(message.chat.id, f, reply_markup=markup, caption=f"Сцена {step} готова. Проверьте качество!")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка генерации видео. Попробуйте еще раз с помощью /run_pipeline")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    username = call.from_user.username
    if not (username and username.lower() in [u.lower() for u in ALLOWED_USERS]): return
    
    session = load_session()
    step = session["current_step"]
    chat_id = call.message.chat.id
    
    if call.data == "approve_step":
        bot.answer_callback_query(call.id, "Сцена одобрена!")
        bot.send_message(chat_id, "✂️ Извлекаю последний кадр для следующей сцены...")
        
        video_path = f"temp_build/veo_{step}.mp4"
        last_frame = f"temp_build/face_after_{step}.png"
        
        if extract_last_frame(video_path, last_frame):
            session["face_image"] = last_frame
            # Отправляем последний кадр в чат, чтобы пользователь видел опорную картинку
            with open(last_frame, "rb") as f:
                bot.send_photo(chat_id, f, caption=f"Опорный кадр после Сцены {step}. Он будет использован для Сцены {step+1}.")
        
        session["current_step"] = step + 1
        save_session(session)
        
        if session["current_step"] <= len(SCENARIO):
            bot.send_message(chat_id, f"👉 Нажмите /run_pipeline чтобы сгенерировать Сцену {session['current_step']}.")
        else:
            bot.send_message(chat_id, "🎉 Поздравляем! Все сцены успешно сгенерированы!")
            
    elif call.data == "redo_step":
        bot.answer_callback_query(call.id, "Перегенерация...")
        # Удаляем старый файл, чтобы сгенерировать заново
        video_path = f"temp_build/veo_{step}.mp4"
        if os.path.exists(video_path): os.remove(video_path)
        bot.send_message(chat_id, "Сбросил кэш. Запускаю генерацию заново...")
        start_pipeline(call.message)

@bot.message_handler(commands=['reset'])
def reset_session(message):
    if not check_access(message): return
    save_session({"current_step": 1, "face_image": "studio_face.png"})
    # Очищаем папку temp_build
    os.system("rm -rf temp_build/*")
    bot.reply_to(message, "🔄 Сессия полностью сброшена! Начинаем со Сцены 1. Введите /run_pipeline")

print("🤖 Сценарный интерактивный бот запущен.")
bot.polling(none_stop=True)
