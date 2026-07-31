import os
import sys
import json
import time
import subprocess
import traceback
import requests
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/telegram_agent_bot.log", rotation="10 MB", retention="7 days", level="INFO")

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("ANTIGRAVITY_BOT_TOKEN")
ALLOWED_USER_ID_STR = os.getenv("ALLOWED_TELEGRAM_USER_ID") or os.getenv("TG_CHAT_ID_MAIN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка ключей
if not TELEGRAM_BOT_TOKEN:
    logger.error("Критическая ошибка: TELEGRAM_BOT_TOKEN и ANTIGRAVITY_BOT_TOKEN не заданы в .env!")
if not ALLOWED_USER_ID_STR:
    logger.error("Критическая ошибка: ALLOWED_TELEGRAM_USER_ID и TG_CHAT_ID_MAIN не заданы в .env!")
if not OPENAI_API_KEY:
    logger.error("Критическая ошибка: OPENAI_API_KEY не задан в .env!")

ALLOWED_TELEGRAM_USER_ID = int(ALLOWED_USER_ID_STR) if ALLOWED_USER_ID_STR else None

# Инициализация клиента OpenAI
openai_client = None
if OPENAI_API_KEY:
    clean_key = OPENAI_API_KEY.strip().rstrip('.')
    openai_client = OpenAI(api_key=clean_key)

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ограничение истории диалога
MAX_HISTORY = 20
chat_history = []

# --- Определение инструментов для ИИ ---

def run_command(command):
    """Выполняет shell-команду в рабочей директории"""
    logger.info(f"Выполнение команды: {command}")
    try:
        # Запускаем в рабочей директории проекта
        res = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=WORKSPACE_DIR,
            timeout=120
        )
        return {
            "stdout": res.stdout[:5000],  # обрезаем длинный вывод
            "stderr": res.stderr[:2000],
            "returncode": res.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Превышено время ожидания выполнения команды (120 секунд)."}
    except Exception as e:
        return {"error": str(e)}

def read_file(filepath):
    """Читает содержимое текстового файла"""
    logger.info(f"Чтение файла: {filepath}")
    full_path = os.path.join(WORKSPACE_DIR, filepath)
    # Защита от выхода за пределы воркспейса
    if not os.path.abspath(full_path).startswith(os.path.abspath(WORKSPACE_DIR)):
        return {"error": "Доступ запрещен: путь выходит за пределы воркспейса."}
    
    if not os.path.exists(full_path):
        return {"error": f"Файл {filepath} не найден."}
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(8000)  # Читаем первые 8к символов
            return {"content": content, "truncated": len(content) >= 8000}
    except Exception as e:
        return {"error": str(e)}

def write_file(filepath, content):
    """Записывает контент в файл"""
    logger.info(f"Запись в файл: {filepath}")
    full_path = os.path.join(WORKSPACE_DIR, filepath)
    if not os.path.abspath(full_path).startswith(os.path.abspath(WORKSPACE_DIR)):
        return {"error": "Доступ запрещен: путь выходит за пределы воркспейса."}
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": f"Файл {filepath} успешно записан."}
    except Exception as e:
        return {"error": str(e)}

def list_dir(dirpath):
    """Показывает список файлов в указанной директории"""
    logger.info(f"Просмотр папки: {dirpath}")
    full_path = os.path.join(WORKSPACE_DIR, dirpath)
    if not os.path.abspath(full_path).startswith(os.path.abspath(WORKSPACE_DIR)):
        return {"error": "Доступ запрещен: путь выходит за пределы воркспейса."}
    
    if not os.path.exists(full_path):
        return {"error": f"Директория {dirpath} не найдена."}
    
    try:
        items = os.listdir(full_path)
        result = []
        for item in items:
            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            size = os.path.getsize(item_path) if not is_dir else 0
            result.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size_bytes": size
            })
        return {"items": result}
    except Exception as e:
        return {"error": str(e)}

def add_rnp_entry(revenue, leads, lever, blocker):
    """Записывает дневную метрику в rnp_log.md"""
    logger.info(f"Запись РНП: Выручка={revenue}, Лиды={leads}")
    log_path = os.path.join(WORKSPACE_DIR, "07_Personal_OS/management/rnp_log.md")
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    header = (
        "# 📊 Хронология РНП (Журнал продаж)\n\n"
        "| Дата | Выручка (руб) | Новые лиды | Главное действие (Рычаг) | Что мешало |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    
    row = f"| {date_str} | {revenue:,} | {leads} | {lever} | {blocker} |\n"
    
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_exists = os.path.exists(log_path)
        
        # Если файл пустой или не существует, пишем заголовок
        if not file_exists or os.path.getsize(log_path) < 10:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(header)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(row)
            
        return {
            "status": "success",
            "message": f"Запись РНП от {date_str} добавлена.",
            "row": row
        }
    except Exception as e:
        logger.error(f"Ошибка записи в РНП: {e}")
        return {"error": str(e)}

def post_stories(media_path, caption="", platforms="whatsapp,telegram", tg_target="me"):
    """Публикует картинку или видео в сторис выбранных платформ"""
    logger.info(f"Запрос на публикацию сторис: {media_path} на платформы {platforms}")
    # Вызываем через subprocess для изоляции
    cmd = f"python smm_brand_ai/publishers/publish_manager.py --media '{media_path}' --caption '{caption}' --platforms '{platforms}' --tg_target '{tg_target}'"
    return run_command(cmd)

def run_smm_trackers(limit=10):
    """Запускает сбор ежедневной статистики со всех соцсетей"""
    logger.info("Запуск SMM трекеров аналитики из Telegram бота...")
    cmd = f"python smm_brand_ai/trackers/run_trackers.py --limit {limit}"
    return run_command(cmd)

def generate_smm_content_plan():
    """Генерирует контент-план на 7 дней на основе аналитики вовлеченности"""
    logger.info("Запуск генератора контент-плана из Telegram бота...")
    cmd = "python smm_brand_ai/planner/ai_content_planner.py"
    return run_command(cmd)

def analyze_creative_reference(ref_text, our_script, title="ref_video", platform="reels", views=0):
    """Анализирует видео-референс конкурента и сравнивает с нашим сценарием"""
    logger.info(f"Запуск анализа креатива '{title}'...")
    try:
        from smm_brand_ai.planner.creative_analyzer import CreativeAnalyzer
        analyzer = CreativeAnalyzer()
        meta = {"title": title, "platform": platform, "views": int(views)}
        result = analyzer.analyze_reference(ref_text, our_script, meta)
        return {"status": "success", "analysis": result}
    except Exception as e:
        logger.error(f"Ошибка вызова CreativeAnalyzer: {e}")
        return {"error": str(e)}

# --- Маппинг функций ---
FUNCTIONS_MAP = {
    "run_command": run_command,
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
    "add_rnp_entry": add_rnp_entry,
    "post_stories": post_stories,
    "run_smm_trackers": run_smm_trackers,
    "generate_smm_content_plan": generate_smm_content_plan,
    "analyze_creative_reference": analyze_creative_reference
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Выполнить shell-команду на компьютере Mac в рабочей директории проекта.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Терминальная команда (например, 'python 06_Scripts_and_Tools/daily_leadgen.py')"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Прочитать текстовый файл в проекте.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Путь относительно корня (например, 'docs/log.md')"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Создать или перезаписать файл.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Путь относительно корня"
                    },
                    "content": {
                        "type": "string",
                        "description": "Новое содержимое файла"
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "Вывести список файлов в папке.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Путь относительно корня проекта"
                    }
                },
                "required": ["dirpath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_rnp_entry",
            "description": "Добавить запись в РНП: выручка, лиды, рычаг (действие дня) и мешающий фактор.",
            "parameters": {
                "type": "object",
                "properties": {
                    "revenue": {
                        "type": "number",
                        "description": "Выручка за день в рублях (число)"
                    },
                    "leads": {
                        "type": "number",
                        "description": "Количество новых квалифицированных лидов"
                    },
                    "lever": {
                        "type": "string",
                        "description": "Главное действие дня, принесшее пользу (рычаг)"
                    },
                    "blocker": {
                        "type": "string",
                        "description": "Что мешало работе (нож/пуля)"
                    }
                },
                "required": ["revenue", "leads", "lever", "blocker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "post_stories",
            "description": "Опубликовать картинку или видео в сторис (статусы) соцсетей (WhatsApp, Telegram, Instagram).",
            "parameters": {
                "type": "object",
                "properties": {
                    "media_path": {
                        "type": "string",
                        "description": "Абсолютный путь к файлу медиа на Mac (9:16)"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Текст/подпись к истории"
                    },
                    "platforms": {
                        "type": "string",
                        "description": "Платформы через запятую. Допустимо: 'whatsapp', 'telegram', 'instagram' (по умолчанию 'whatsapp,telegram')"
                    },
                    "tg_target": {
                        "type": "string",
                        "description": "Telegram ID или 'me' для личного профиля (по умолчанию 'me')"
                    }
                },
                "required": ["media_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_smm_trackers",
            "description": "Запустить сбор ежедневной аналитики и статистики со всех соцсетей (просмотры, лайки, комменты).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Лимит постов для сбора (по умолчанию 10)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_smm_content_plan",
            "description": "Сгенерировать ИИ контент-план на 7 дней на основе показателей прошлой вовлеченности контента.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_creative_reference",
            "description": "Сравнить наш сценарий видео с успешным референсом конкурента, получить разбор хуков, структуры и финальный готовый сценарий ролика.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref_text": {
                        "type": "string",
                        "description": "Текст или транскрипт видео конкурента (референс)"
                    },
                    "our_script": {
                        "type": "string",
                        "description": "Наш текущий сценарий или описание ролика, который мы хотим улучшить"
                    },
                    "title": {
                        "type": "string",
                        "description": "Заголовок/тема видео (по умолчанию 'ref_video')"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Платформа референса (reels, shorts, tiktok)"
                    },
                    "views": {
                        "type": "number",
                        "description": "Просмотры референса (если известны)"
                    }
                },
                "required": ["ref_text", "our_script"]
            }
        }
    }
]

def download_telegram_file(file_id, dest_path):
    url_file_info = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    try:
        res = requests.get(url_file_info, timeout=10)
        res.raise_for_status()
        file_path_tg = res.json().get("result", {}).get("file_path")
        if file_path_tg:
            url_download = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path_tg}"
            res_data = requests.get(url_download, timeout=60)
            res_data.raise_for_status()
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(res_data.content)
            return True
    except Exception as e:
        logger.error(f"Ошибка скачивания файла {file_id}: {e}")
    return False

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram: {e}")

def send_chat_action(chat_id, action="typing"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": action}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

# --- Обработка диалога с ИИ-Агентом ---

def process_message_with_ai(user_message):
    global chat_history
    
    system_prompt = (
        "Вы — Antigravity (Cline), автономный ИИ-ассистент разработчика и предпринимателя.\n"
        "Вы запущены в режиме удаленного Telegram-агента на компьютере Mac пользователя.\n"
        "Ваша цель — помогать пользователю управлять проектами, запускать автоматизации, собирать лидов, "
        "читать и писать файлы проекта, а также вести журнал продаж РНП.\n"
        "Отвечайте кратко, по делу, строго на русском языке.\n"
        "У вас есть доступ к инструментам воркспейса. Используйте их при необходимости."
    )
    
    # Добавляем сообщение пользователя в историю
    chat_history.append({"role": "user", "content": user_message})
    
    # Ограничиваем историю
    if len(chat_history) > MAX_HISTORY:
        chat_history = chat_history[-MAX_HISTORY:]
        
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    
    try:
        # Первый запрос к модели
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            timeout=40
        )
        
        response_message = response.choices[0].message
        
        # Если модель хочет вызвать инструмент
        while response_message.tool_calls:
            tool_calls = response_message.tool_calls
            # Добавляем ответ модели с запросом инструментов в историю диалога для контекста
            messages.append(response_message)
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"ИИ вызывает инструмент {func_name} с аргументами: {func_args}")
                
                # Вызов соответствующей функции
                func_to_call = FUNCTIONS_MAP.get(func_name)
                if func_to_call:
                    tool_result = func_to_call(**func_args)
                else:
                    tool_result = {"error": f"Инструмент {func_name} не найден."}
                
                # Добавляем результат работы инструмента в историю диалога
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # Повторный запрос модели с результатами инструментов
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS_SCHEMA,
                timeout=40
            )
            response_message = response.choices[0].message
            
        # Финальный текстовый ответ от модели
        final_answer = response_message.content
        chat_history.append({"role": "assistant", "content": final_answer})
        return final_answer
        
    except Exception as e:
        logger.error(f"Ошибка в цикле ИИ-агента: {e}")
        logger.error(traceback.format_exc())
        return f"⚠️ Произошла ошибка при обработке запроса: {str(e)}"

# --- Главный цикл Telegram Long Polling ---

def main():
    logger.info("=== Запуск Telegram ИИ-Агента (Long Polling) ===")
    
    if not TELEGRAM_BOT_TOKEN or not ALLOWED_TELEGRAM_USER_ID or not openai_client:
        logger.error("Запуск невозможен. Проверьте переменные TELEGRAM_BOT_TOKEN, ALLOWED_TELEGRAM_USER_ID и OPENAI_API_KEY в файле .env!")
        sys.exit(1)
        
    offset = 0
    
    # Отправим стартовое уведомление
    send_telegram_message(ALLOWED_TELEGRAM_USER_ID, "🚀 *ИИ-Агент Antigravity запущен локально на Mac и готов к командам!*")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code != 200:
                logger.warning(f"Telegram API вернул код {response.status_code}. Ждем 5 сек...")
                time.sleep(5)
                continue
                
            updates = response.json().get("result", [])
            
            for update in updates:
                offset = update["update_id"] + 1
                
                message = update.get("message")
                if not message:
                    continue
                    
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")
                caption = message.get("caption", "")
                
                # Проверка авторизации
                if user_id != ALLOWED_TELEGRAM_USER_ID:
                    logger.warning(f"Неавторизованный доступ от Chat ID {chat_id} (User ID {user_id}). Игнорируем.")
                    # Отправляем один раз заглушку
                    send_telegram_message(chat_id, "🚫 Доступ запрещен. Этот бот является приватным ИИ-агентом.")
                    continue

                # Проверяем наличие медиафайлов
                media_info = ""
                photo = message.get("photo")
                video = message.get("video")
                document = message.get("document")
                
                file_id = None
                file_ext = ""
                
                if photo:
                    file_id = photo[-1]["file_id"]
                    file_ext = ".jpg"
                elif video:
                    file_id = video["file_id"]
                    file_ext = ".mp4"
                elif document:
                    mime = document.get("mime_type", "")
                    if mime.startswith("image/") or mime.startswith("video/"):
                        file_id = document["file_id"]
                        fname = document.get("file_name", "")
                        file_ext = os.path.splitext(fname)[1] or (".jpg" if mime.startswith("image/") else ".mp4")
                
                if file_id:
                    dest_dir = os.path.join(WORKSPACE_DIR, "scratch", "smm_media")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, f"{file_id[:15]}_{int(time.time())}{file_ext}")
                    
                    send_chat_action(chat_id, "upload_document")
                    if download_telegram_file(file_id, dest_path):
                        logger.info(f"Медиафайл успешно скачан: {dest_path}")
                        media_info = f"\n[Прикреплен медиафайл: {dest_path}]"
                        if caption:
                            text = f"{caption} {media_info}"
                        else:
                            text = media_info.strip()
                
                if not text:
                    continue
                    
                logger.info(f"Получено сообщение: {text}")
                
                # Показываем статус «печатает»
                send_chat_action(chat_id, "typing")
                
                if text.strip() == "/start":
                    welcome_text = (
                        "👋 Привет! Я твой локальный ИИ-агент Antigravity.\n\n"
                        "Я могу:\n"
                        "1. **Квалифицированные лиды:** напиши `/leads` для просмотра лидов С КОНТАКТАМИ\n"
                        "2. **Вести РНП:** просто напиши мне 'Запиши в РНП: выручка 15000, 3 лида, рычаг: рассылка'\n"
                        "3. **Запускать скрипты:** например, 'Запусти сбор лидов'\n"
                        "4. **Работать с файлами:** 'Покажи лог' или 'Покажи blockers.md'\n"
                        "5. **Постить сторис:** отправь мне картинку/видео и напиши 'выложи в сторис ватсап и тг'\n\n"
                        "Что делаем сегодня?"
                    )
                    send_telegram_message(chat_id, welcome_text)
                    continue

                if text.strip() == "/leads" or "покажи лидов" in text.lower():
                    send_chat_action(chat_id, "typing")
                    date_today = datetime.now().strftime('%Y-%m-%d')
                    qual_path = f"03_Marketing_and_Sales/daily_leads/{date_today}/leads_qualified.json"
                    
                    if not os.path.exists(qual_path):
                        base_dir = "03_Marketing_and_Sales/daily_leads"
                        if os.path.exists(base_dir):
                            subdirs = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))], reverse=True)
                            if subdirs:
                                qual_path = os.path.join(base_dir, subdirs[0], "leads_qualified.json")
                                
                    if os.path.exists(qual_path):
                        try:
                            with open(qual_path, "r", encoding="utf-8") as f:
                                qual_leads = json.load(f)
                            send_telegram_message(chat_id, f"🎯 *Мульти-канальный LeadGen OS | Горячие лиды: `{len(qual_leads)}`*\nПоказываю лиды с гарантированными контактами:")
                            
                            for idx, lead in enumerate(qual_leads[:7], 1):
                                contacts = []
                                if lead.get("phone"): contacts.append(f"📞 `{lead['phone']}`")
                                if lead.get("whatsapp"): contacts.append(f"📲 [WhatsApp]({lead['whatsapp']})")
                                if lead.get("telegram"): contacts.append(f"✈️ `{lead['telegram']}`")
                                if lead.get("email"): contacts.append(f"✉️ `{lead['email']}`")
                                if lead.get("profile_url"): contacts.append(f"🌐 [Профиль]({lead['profile_url']})")
                                
                                source_badge = f"`[{lead.get('source', 'Multi-Source')}]`"
                                score_val = lead.get('ai_score', 8)
                                score_badge = f"🔥 `{score_val}/10` (Горячий)" if score_val >= 8 else f"⚡ `{score_val}/10` (Теплый)"
                                
                                lead_card = (
                                    f"🎯 *Лид №{idx} | {lead.get('company_name')}*\n"
                                    f"👤 *ЛПР/Автор:* {lead.get('name', 'Не указано')}\n"
                                    f"📍 *Канал:* {source_badge} | *Скоринг:* {score_badge}\n"
                                    f"💡 *Интент:* _{lead.get('intent_type', 'Поиск решений')}_\n\n"
                                    f"📇 *КОНТАКТЫ:* {', '.join(contacts)}\n\n"
                                    f"💬 *ПЕРВОЕ СООБЩЕНИЕ (Адаптировано под канал):*\n_{lead.get('generated_pitch', '')}_"
                                )
                                send_telegram_message(chat_id, lead_card)
                                time.sleep(0.5)
                        except Exception as e:
                            send_telegram_message(chat_id, f"Ошибка чтения квалифицированных лидов: {e}")
                    else:
                        send_telegram_message(chat_id, "⚠️ Квалифицированные лиды за сегодня еще не собраны. Напиши 'запусти лидогенерацию'.")
                    continue
                
                # Обработка сообщения через ИИ
                answer = process_message_with_ai(text)
                send_telegram_message(chat_id, answer)
                
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем.")
            break
        except Exception as e:
            logger.error(f"Ошибка в цикле getUpdates: {e}")
            logger.error(traceback.format_exc())
            time.sleep(5)

if __name__ == "__main__":
    main()
