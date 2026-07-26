import os
import sys
import traceback
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

def send_telegram_alert(text):
    """Отправляет системное сообщение/ошибку в Телеграм"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Даже Телеграм API упал: {e}")

def run_weekly_job():
    """Здесь находится основная логика задачи"""
    # TODO: Тут будет парсинг трендов, анализ и упаковка
    # Для примера имитируем успешное выполнение:
    
    # Если все прошло ок — отправляем успешный отчет (реанимация/статус-кво)
    report_text = (
        "✅ <b>Системный Крон: Успешный запуск!</b>\n\n"
        "Отчет по стикерам за неделю собран и готов.\n"
        "Ошибок не обнаружено. Продолжаю работу в штатном режиме."
    )
    send_telegram_alert(report_text)

if __name__ == "__main__":
    try:
        run_weekly_job()
    except Exception as e:
        # Если скрипт где-то упал (например, сайт с трендами недоступен)
        # Формируем красивый отчет об ошибке с куском кода, где произошел сбой
        error_trace = traceback.format_exc()
        
        # Обрезаем трейсбек, если он слишком длинный (лимит ТГ 4096 символов)
        if len(error_trace) > 3000:
            error_trace = error_trace[-3000:]
            
        alert_msg = (
            "🚨 <b>CRITICAL ERROR В СИСТЕМНОМ КРОНЕ!</b>\n\n"
            "Скрипт еженедельного отчета упал. Лог ошибки:\n"
            f"<pre>{error_trace}</pre>\n\n"
            "<i>Требуется ручная проверка на VPS!</i>"
        )
        send_telegram_alert(alert_msg)
        sys.exit(1)
