#!/bin/bash
# Скрипт деплоя и настройки окружения на VPS (Ubuntu 22.04+)

echo "Начинаем установку зависимостей для B2B Lead System..."

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv curl wget git cron

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей Python
pip install --upgrade pip
pip install -r parsers/requirements.txt
pip install httpx playwright python-dotenv openai vertexai supabase

# Установка браузеров для Playwright (необходимо для Госзакупок и Uchet.kz)
playwright install
playwright install-deps

# Проверка наличия .env файла
if [ ! -f "../../../.env" ]; then
    echo "ВНИМАНИЕ: Файл .env не найден в корне проекта! Создайте его перед запуском."
fi

# Настройка прав для скрипта запуска
chmod +x run_hourly_pipeline.sh

echo "Установка завершена! Чтобы добавить пайплайн в cron, выполните:"
echo "(crontab -l 2>/dev/null; echo \"0 * * * * cd $(pwd) && ./run_hourly_pipeline.sh >> /var/log/b2b_lead_system.log 2>&1\") | crontab -"
