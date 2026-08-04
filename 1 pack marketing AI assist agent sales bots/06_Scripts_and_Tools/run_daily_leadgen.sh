#!/bin/zsh

# Путь к рабочей директории проекта
PROJECT_DIR="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
cd "$PROJECT_DIR"

# Настройка путей, чтобы все системные утилиты и python были доступны
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Проверяем наличие файла .env
# Переменные окружения автоматически загружаются внутри Python с помощью python-dotenv

echo "=== [$(date)] Запуск ежедневного сбора контактов ==="

# Запуск основного пайплайна сбора контактов
"/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.venv/bin/python" 03_Marketing_and_Sales/daily_lead_harvester/main.py --now

echo "=== [$(date)] Сбор контактов завершен ==="
