import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
OUTPUT_BASE_DIR = PROJECT_ROOT / "03_Marketing_and_Sales" / "daily_leads"

# Ключевые поисковые запросы по требованиям пользователя
TARGET_QUERIES = [
    "ии",
    "разработка",
    "боты",
    "маркетинг",
    "контекстная реклама",
    "ии контент"
]

# Запросы для HH (расширенные русские и английские термины)
HH_QUERIES = [
    "искусственный интеллект",
    "разработка ботов",
    "telegram бот",
    "маркетолог",
    "контекстная реклама",
    "яндекс директ",
    "генерация контента",
    "нейросети"
]

# Запросы для Threads.net
THREADS_QUERIES = [
    "ищу разработку ботов",
    "нужен маркетолог",
    "нужна контекстная реклама",
    "кто умеет создавать ии контент",
    "ищем разработчика чат ботов",
    "нужен ии интегратор"
]

# Регионы HH
HH_REGIONS = {
    "hh.kz": 40,   # Казахстан
    "hh.ru": 113   # Россия
}

# Телеграм бот для отправки готового ежедневного отчета (из .env)
TELEGRAM_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN", "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT_ID_MAIN", "888005446")
