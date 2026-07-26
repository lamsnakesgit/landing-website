#!/bin/bash
# Скрипт для ежедневного запуска лидогенерации на Mac

# Переходим в рабочую директорию проекта
cd "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots" || exit 1

# Создаем папку для логов, если её нет
mkdir -p logs

# Загружаем переменные окружения из .env
if [ -f .env ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    # Убираем пробелы в начале и конце
    line=$(echo "$line" | xargs)
    # Пропускаем пустые строки и комментарии
    if [[ -n "$line" && ! "$line" =~ ^# ]]; then
      export "$line"
    fi
  done < .env
fi

echo "$(date): === Старт ежедневного конвейера лидогенерации ===" >> logs/pipeline.log

# Шаг 1. Сбор лидов через Playwright (adata.kz, hh.ru, hh.kz, threads.net)
echo "$(date): Шаг 1. Запуск Playwright скрапера..." >> logs/pipeline.log
"/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.venv/bin/python" scripts/playwright_leadgen.py >> logs/pipeline.log 2>&1
PLAYWRIGHT_STATUS=$?

if [ $PLAYWRIGHT_STATUS -ne 0 ]; then
  echo "$(date): Ошибка на Шаге 1 (Playwright скрапер). Код выхода: $PLAYWRIGHT_STATUS" >> logs/pipeline.log
  exit $PLAYWRIGHT_STATUS
fi

# Шаг 2. ИИ-обогащение, генерация предложений, сохранение и отправка отчетов
echo "$(date): Шаг 2. Запуск ИИ-обогащения и отправки отчетов..." >> logs/pipeline.log
"/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.venv/bin/python" 06_Scripts_and_Tools/daily_leadgen.py >> logs/pipeline.log 2>&1
LEADGEN_STATUS=$?

if [ $LEADGEN_STATUS -ne 0 ]; then
  echo "$(date): Ошибка на Шаге 2 (ИИ-обогащение). Код выхода: $LEADGEN_STATUS" >> logs/pipeline.log
  exit $LEADGEN_STATUS
fi

echo "$(date): === Конвейер успешно завершен! ===" >> logs/pipeline.log
