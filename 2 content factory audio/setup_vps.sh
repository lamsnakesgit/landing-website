#!/bin/bash

# Скрипт автоматической настройки VPS для Veo Content Factory
# Предназначен для Ubuntu 22.04+

echo "🚀 Начинаю настройку окружения на VPS..."

# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python и FFmpeg
echo "📦 Установка Python, Pip и FFmpeg..."
sudo apt install -y python3 python3-pip ffmpeg tmux

# 3. Создание виртуального окружения
echo "🐍 Настройка виртуального окружения Python..."
python3 -m venv venv
source venv/bin/activate

# 4. Установка зависимостей
if [ -f "requirements.txt" ]; then
    echo "📥 Установка библиотек из requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ Файл requirements.txt не найден. Устанавливаю базу вручную..."
    pip install google-genai python-dotenv requests
fi

echo "✅ Настройка завершена!"
echo "💡 Для запуска в фоне используй: tmux new -s veo_production"
echo "💡 Затем внутри tmux: source venv/bin/activate && python3 scripts/produce_with_logs.py"
echo "💡 Чтобы выйти из tmux (но оставить скрипт работать): Ctrl+B, затем D"
