#!/usr/bin/env bash
# Ежедневный запуск автосбора лидов (adata.kz, hh.ru, hh.kz, threads.net)
# Запросы: ии, разработка, боты, маркетинг, контекстная реклама, ии контент

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

export PYTHONPATH="$SCRIPT_DIR/parsers:$PYTHONPATH"

LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

DATE_STR=$(date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/daily_leads_$DATE_STR.log"

echo "==========================================" | tee -a "$LOG_FILE"
echo "🚀 Запуск daily leadgen pipeline: $DATE_STR" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/parsers/daily_lead_aggregator.py" 2>&1 | tee -a "$LOG_FILE"

echo "✅ Завершено. Результаты сохранены в 03_Marketing_and_Sales/daily_leads/$DATE_STR" | tee -a "$LOG_FILE"
