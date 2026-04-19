import os
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logger.info("=== SMOKE TEST: SUPABASE ===")
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Ключи не найдены в .env файле!")
    exit(1)

try:
    logger.info(f"Пробуем подключиться к {SUPABASE_URL}...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Пытаемся забрать 1 элемент из таблицы leads (даже если таблица пуста, запрос должен пройти без ошибок)
    response = supabase.table("leads").select("*").limit(1).execute()
    
    logger.success("✅ УСПЕХ! Подключение к БД работает!")
    if response.data:
        logger.info(f"Найдено лидов: {len(response.data)}")
    else:
        logger.info("Таблица `leads` существует, но пока пуста (это нормально).")
        
    # Пробуем вставить тестовую запись (Smoke test записи)
    test_lead = {
        "company_name": "Test Company Yekaterinburg",
        "phone": "77000000000",
        "source": "smoke_test",
        "status": "new"
    }
    
    logger.info("Пытаемся сделать тестовую запись в базу...")
    insert_response = supabase.table("leads").insert(test_lead).execute()
    logger.success(f"✅ УСПЕХ! Тестовый лид записан! ПРАВА НА ЗАПИСЬ ЕСТЬ.")
    
except Exception as e:
    logger.error(f"❌ ОШИБКА SMOKE ТЕСТА: {e}")
    logger.error("Возможно, ты не запустил файл init_supabase.sql, или используешь anon-ключ вместо service_role ключа.")
