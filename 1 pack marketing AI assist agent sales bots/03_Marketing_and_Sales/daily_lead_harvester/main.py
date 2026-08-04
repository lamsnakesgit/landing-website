import sys
import time
import argparse
import logging
import requests
from pathlib import Path
from datetime import datetime

from config import TARGET_QUERIES, HH_QUERIES, THREADS_QUERIES, OUTPUT_BASE_DIR, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from parsers import run_all_parsers
from ai_copywriter import generate_lead_draft_and_offer
from exporter import export_daily_leads
import schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DailyLeadHarvester")

def send_telegram_notification(excel_path, total_count, folder_path):
    """
    Отправка файла Excel с лидами за день в Telegram пользователю
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.info("Telegram токен или Chat ID не задан, пропускаем отправку.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    caption = (
        f"🚀 **Ежедневный Сбор Лидов Завершен!**\n\n"
        f"📅 **Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"📊 **Всего собрано контактов**: {total_count}\n"
        f"🌐 **Источники**: `adata.kz`, `hh.ru`, `hh.kz`, `threads.net`\n"
        f"🎯 **Темы**: ИИ, Разработка, Боты, Маркетинг, Контекст, ИИ-контент\n\n"
        f"📁 Результаты и готовые драфты сообщений сохранены в файле ниже."
    )

    try:
        with open(excel_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
            resp = requests.post(url, data=data, files=files, timeout=30)
            if resp.status_code == 200:
                logger.info("✅ Уведомление и Excel отчёт отправлены в Telegram!")
            else:
                logger.warning(f"Не удалось отправить документ в Telegram: {resp.text}")
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")

def run_lead_harvest_job():
    """
    Основная задача сбора лидов
    """
    logger.info("==================================================")
    logger.info("🚀 ЗАПУСК ЕЖЕДНЕВНОГО СБОРА ЛИДОВ И ОФФЕРОВ")
    logger.info("==================================================")

    queries_dict = {
        "targets": TARGET_QUERIES,
        "hh": HH_QUERIES,
        "threads": THREADS_QUERIES
    }

    # 1. Запуск парсеров по 4 источникам
    raw_leads = run_all_parsers(queries_dict)
    logger.info(f"📥 Собрано сырых лидов со всех источников: {len(raw_leads)}")

    if not raw_leads:
        logger.warning("⚠️ Лидов не найдено. Проверьте подключение к сети.")
        return

    # 2. Обогащение лидов: генерация драфтов 1-го сообщения и офферов
    processed_leads = []
    for idx, lead in enumerate(raw_leads, 1):
        ai_data = generate_lead_draft_and_offer(lead)
        lead["niche"] = ai_data["niche"]
        lead["draft_message"] = ai_data["draft_message"]
        lead["offer_proposal"] = ai_data["offer_proposal"]
        processed_leads.append(lead)

    # 3. Экспорт данных в папку дня
    result = export_daily_leads(processed_leads, OUTPUT_BASE_DIR)

    # 4. Отправка отчета в Telegram
    send_telegram_notification(result["xlsx"], result["count"], result["folder"])

    logger.info("==================================================")
    logger.info("✅ ЕЖЕДНЕВНЫЙ ЦИКЛ СБОРА УСПЕШНО ЗАВЕРШЕН!")
    logger.info("==================================================")

def main():
    parser = argparse.ArgumentParser(description="Daily Lead & Offer Harvester")
    parser.add_argument("--now", action="store_true", help="Запустить сбор немедленно один раз")
    parser.add_argument("--schedule", action="store_true", help="Запустить в режиме планировщика (ежедневно в 09:00)")
    args = parser.parse_args()

    if args.schedule:
        logger.info("⏰ Планировщик запущен. Сбор будет производиться ежедневно в 09:00.")
        schedule.every().day.at("09:00").do(run_lead_harvest_job)
        
        # Выполним первичный сбор при запуске
        run_lead_harvest_job()
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # По умолчанию при запуске выполняется разовый сбор
        run_lead_harvest_job()

if __name__ == "__main__":
    main()
