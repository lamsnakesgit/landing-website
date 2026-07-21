#!/bin/bash
# Запуск ежедневного/ежечасного пайплайна лидогенерации и аутрича
# Запускается через cron

# Определение директорий
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=================================================="
echo "Время запуска: $(date)"
echo "Запуск пайплайна..."

# Активация виртуального окружения
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "ВНИМАНИЕ: Виртуальное окружение не найдено! Запуск системным python3."
fi

# 1. Запуск парсеров, обогащения и ИИ-офферов
echo "[1/2] Запуск Агрегатора Лидов (Сбор -> Обогащение -> ИИ)..."
export PYTHONPATH="$SCRIPT_DIR/parsers:$PYTHONPATH"
python3 "$SCRIPT_DIR/parsers/daily_lead_aggregator.py"

# 2. Запуск модуля Outreach (Отправка сообщений)
echo "[2/2] Запуск модуля автоматического Аутрича..."
python3 "$SCRIPT_DIR/outreach_sender.py"

echo "Пайплайн успешно завершен: $(date)"
echo "=================================================="
