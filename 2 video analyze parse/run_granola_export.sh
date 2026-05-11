#!/bin/bash

# Путь к директории проекта
PROJECT_DIR="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 video analyze parse"

# Переход в рабочую директорию
cd "$PROJECT_DIR" || exit

# Загрузка переменных окружения и запуск скрипта
# Используем полный путь к python3 (обычно /usr/bin/python3 или /usr/local/bin/python3)
/usr/bin/python3 export_granola_to_notion.py >> "$PROJECT_DIR/logs/granola_export.log" 2>&1
