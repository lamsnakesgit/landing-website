"""
Скрипт рассылки по базе доставок еды через Evolution API.
Запускается по крону на VPS в 9:00.
Читает базу из JSON-файла, отправляет по расписанию с паузами.
"""

import json
import os
import time
import random
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === КОНФИГУРАЦИЯ ===
EVOLUTION_BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://evolutionapi.aiconicvibe.store")
EVOLUTION_API_KEY  = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "instance1")  # Имя инстанса в Evolution

LEADS_FILE    = Path(__file__).parent / "food_delivery_leads.json"
SENT_LOG_FILE = Path(__file__).parent / "sent_log.json"

MIN_DELAY = 60   # Минимум секунд между сообщениями (анти-бан)
MAX_DELAY = 120  # Максимум секунд
DAILY_LIMIT = 30 # Максимум сообщений за один запуск

# === ТЕКСТ СООБЩЕНИЯ (персонализируется по имени) ===
def build_message(lead: dict) -> str:
    name = lead.get("name", "")
    city = lead.get("city", "Казахстан")

    return f"""Привет! 👋

Нашел вас в Instagram/2ГИС как доставку {city}. Смотрю — заказы принимаете через WhatsApp вручную. Это работает, но при росте объема становится сложно.

Мы делаем интерактивные QR-меню для доставки еды — это мини-сайт, который открывается за 1 секунду. Клиент выбирает блюда и нажимает «Заказать» — у вас в WhatsApp уже готовый список с суммой. Никаких "а что у вас есть?" и прайсов картинками.

Плюс — каждый клиент, открывший меню, попадает в базу ретаргетинга для будущих акций.

Для вас сделаем демо-версию с вашим меню за 1 день — посмотрите как выглядит, ничего не нужно решать заранее.

Интересно глянуть?"""


def load_leads() -> list:
    """Загружает лидов из JSON, возвращает только со статусом 'new' и с телефоном."""
    if not LEADS_FILE.exists():
        print(f"[ERROR] Файл {LEADS_FILE} не найден.")
        return []
    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        all_leads = json.load(f)
    return [l for l in all_leads if l.get("status") == "new" and l.get("phone")]


def load_sent_log() -> set:
    """Загружает список уже отправленных номеров."""
    if not SENT_LOG_FILE.exists():
        return set()
    with open(SENT_LOG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("sent_phones", []))


def save_sent_log(sent_phones: set):
    """Сохраняет обновленный список отправленных."""
    with open(SENT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"sent_phones": list(sent_phones)}, f, ensure_ascii=False, indent=2)


def update_lead_status(phone: str, new_status: str):
    """Обновляет статус лида в JSON-файле."""
    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        leads = json.load(f)
    for lead in leads:
        if lead.get("phone") == phone:
            lead["status"] = new_status
            lead["contacted_at"] = datetime.now().isoformat()
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)


def send_wa_message(phone: str, text: str) -> bool:
    """Отправляет сообщение через Evolution API."""
    clean_phone = "".join(filter(str.isdigit, phone))
    url = f"{EVOLUTION_BASE_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": clean_phone,
        "options": {
            "delay": random.randint(2000, 4000),  # Имитация печати
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": text
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"  [OK] Отправлено на {phone}")
        return True
    except requests.RequestException as e:
        print(f"  [FAIL] Evolution API ошибка для {phone}: {e}")
        return False


def run():
    print(f"\n=== Запуск рассылки {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    if not EVOLUTION_API_KEY:
        print("[ERROR] EVOLUTION_API_KEY не задан в .env. Выход.")
        return

    leads     = load_leads()
    sent_log  = load_sent_log()

    if not leads:
        print("[INFO] Нет новых лидов с телефонами для отправки. Выход.")
        return

    print(f"[INFO] Всего лидов к отправке: {len(leads)} (лимит: {DAILY_LIMIT})")

    sent_count = 0
    for lead in leads:
        if sent_count >= DAILY_LIMIT:
            print(f"[STOP] Достигнут дневной лимит {DAILY_LIMIT} сообщений.")
            break

        phone = lead["phone"]

        if phone in sent_log:
            print(f"  [SKIP] {phone} — уже отправлялось ранее.")
            continue

        message = build_message(lead)
        print(f"\n-> {lead['name']} ({lead['city']}) | {phone}")

        success = send_wa_message(phone, message)

        if success:
            sent_log.add(phone)
            save_sent_log(sent_log)
            update_lead_status(phone, "contacted")
            sent_count += 1

            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"  [PAUSE] Ждем {delay}с до следующего сообщения...")
            time.sleep(delay)
        else:
            update_lead_status(phone, "failed")

    print(f"\n=== Рассылка завершена: отправлено {sent_count} сообщений ===")


if __name__ == "__main__":
    run()
