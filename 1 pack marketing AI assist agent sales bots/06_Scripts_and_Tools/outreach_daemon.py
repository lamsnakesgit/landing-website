import time
import random
import requests
from loguru import logger
from supabase import create_client, Client

# =====================================================================
# КОНФИГУРАЦИЯ (Сюда нужно вставить ключи после того как настроишь)
# =====================================================================
SUPABASE_URL = "https://твоя-база.supabase.co"
SUPABASE_KEY = "ТВОЙ_КЛЮЧ"
EVOLUTION_BASE_URL = "https://evolutionapi.aiconicvibe.store"
EVOLUTION_API_KEY = "ТВОЙ_GLOBAL_API_KEY"

# Пул твоих инстансов (номеров). 
# Скрипт будет по кругу переключать номера, чтобы не словить спам-блок.
INSTANCES_POOL = ["instance_1", "instance_2", "instance_3"]

# Базовые настройки безопасности
MIN_DELAY = 45   # Минимальная пауза между рассылками (сек)
MAX_DELAY = 140  # Максимальная пауза (сек)
BATCH_SIZE = 5   # Сколько лидов забирать за раз

# =====================================================================
# ИНИЦИАЛИЗАЦИЯ
# =====================================================================
logger.add("logs/outreach_daemon.log", rotation="50 MB", retention="10 days", level="INFO")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.warning("Supabase не настроен (или ключи пустые). Демо-режим.")

def get_pending_leads():
    """Забирает лидов из Супабейза, у которых статус 'enriched' (уже написан pitch)"""
    try:
        response = supabase.table("leads").select("*").eq("status", "enriched").limit(BATCH_SIZE).execute()
        return response.data
    except Exception as e:
        logger.error(f"Ошибка чтения Supabase: {e}")
        return []

def mark_lead_status(lead_id, new_status):
    """Обновляет статус лида в БД"""
    try:
        supabase.table("leads").update({"status": new_status}).eq("id", lead_id).execute()
    except Exception as e:
        logger.error(f"Ошибка обновления статуса лида {lead_id}: {e}")

def send_wa_message(target_number, text, instance_name):
    """Отправляет запрос на Evolution API"""
    url = f"{EVOLUTION_BASE_URL}/message/sendText/{instance_name}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Регулярки и чистка номера (оставляем только цифры)
    clean_number = ''.join(filter(str.isdigit, target_number))
    
    payload = {
        "number": clean_number,
        "options": {
            "delay": random.randint(1500, 3000), # Долгая имитация "печатает..."
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Сбой Evolution API: {e}")
        return False

def run_outreach_cycle():
    """Главный цикл рассылки"""
    logger.info("Проверка новых enriched лидов...")
    
    # Для теста без реального Supabase обрываем здесь
    if SUPABASE_URL == "https://твоя-база.supabase.co":
        logger.info("КЛЮЧИ ПОКА НЕ ВВЕДЕНЫ. Жду когда хозяин пропишет инфу.")
        return
        
    leads = get_pending_leads()
    if not leads:
        logger.info("Очередь пуста. Отдыхаем...")
        return
        
    logger.info(f"Найдено {len(leads)} лидов для отправки.")
    
    current_instance_idx = 0
    
    for lead in leads:
        # Круговая ротация номеров (Round Robin)
        active_instance = INSTANCES_POOL[current_instance_idx]
        current_instance_idx = (current_instance_idx + 1) % len(INSTANCES_POOL)
        
        phone = lead.get("phone")
        pitch = lead.get("generated_pitch")
        
        if not phone or not pitch:
            mark_lead_status(lead["id"], "error")
            continue
            
        logger.info(f"[{active_instance}] Отправка на {phone}...")
        
        # Отправка
        success = send_wa_message(phone, pitch, active_instance)
        
        if success:
            mark_lead_status(lead["id"], "contacted")
            logger.success(f"Сообщение доставлено на {phone} через {active_instance}")
            
            # Важнейший этап: случайная задержка (Анти-Бан)
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f"Спим {delay} секунд перед следующим сообщением для безопасности...")
            time.sleep(delay)
        else:
            mark_lead_status(lead["id"], "failed")
            logger.error(f"Не удалось отправить на {phone} с инстанса {active_instance}")

if __name__ == "__main__":
    logger.info("=== Запуск Daemon рассылок (Outreach Engine) ===")
    logger.info(f"Режим Анти-бана: Имитация ввода, Ротация {len(INSTANCES_POOL)} номеров, Паузы {MIN_DELAY}-{MAX_DELAY}с")
    
    while True:
        run_outreach_cycle()
        logger.info("Цикл завершен, ожидание 5 минут до проверки новой партии...")
        time.sleep(300) # Проверяем БД раз в 5 минут
