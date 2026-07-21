"""
Модуль автоматической отправки сообщений (Outreach)
Скрипт проверяет базу (Supabase) на наличие новых лидов с готовыми ИИ-офферами,
отправляет их в n8n webhook (для пересылки в WhatsApp/Telegram),
и обновляет статусы KPI.

Запуск: python outreach_sender.py
"""

import os
import json
import asyncio
import logging
import httpx
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Загружаем переменные окружения
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/outreach-send")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

async def fetch_pending_leads() -> list:
    """Получает лидов, готовых к отправке."""
    # Предполагается, что в таблице companies есть outreach_status и draft_pitch
    query = f"{SUPABASE_URL}/rest/v1/companies?outreach_status=eq.pending&draft_pitch=not.is.null&phone=not.is.null"
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(query, headers=SUPABASE_HEADERS)
        if resp.status_code != 200:
            log.error(f"Ошибка получения лидов из Supabase: {resp.text}")
            return []
        return resp.json()

async def update_lead_status(company_id: str, status: str):
    """Обновляет статус KPI в базе."""
    url = f"{SUPABASE_URL}/rest/v1/companies?external_id=eq.{company_id}"
    payload = {"outreach_status": status, "last_outreach_at": datetime.utcnow().isoformat()}
    
    headers = SUPABASE_HEADERS.copy()
    headers["Prefer"] = "return=minimal"
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.patch(url, headers=headers, json=payload)
        if resp.status_code not in (200, 204):
            log.error(f"Ошибка обновления статуса {company_id}: {resp.text}")

async def send_to_n8n(lead: dict) -> bool:
    """Отправляет лида в n8n webhook для рассылки."""
    payload = {
        "company_id": lead.get("external_id"),
        "company_name": lead.get("name"),
        "phone": lead.get("phone"),
        "message": lead.get("draft_pitch"),
        "platform": "whatsapp" # Можно расширить логику выбора платформы
    }
    
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(N8N_WEBHOOK_URL, json=payload)
            if resp.status_code in (200, 201, 204):
                log.info(f"Успешно отправлено в n8n для: {payload['company_name']}")
                return True
            else:
                log.warning(f"N8N вернул статус {resp.status_code} для {payload['company_name']}")
                return False
        except Exception as e:
            log.error(f"Ошибка соединения с n8n: {e}")
            return False

async def process_outreach():
    log.info("Запуск модуля автоматического Outreach...")
    leads = await fetch_pending_leads()
    
    if not leads:
        log.info("Нет новых лидов со статусом 'pending' для отправки.")
        return

    log.info(f"Найдено лидов для отправки: {len(leads)}")
    
    for lead in leads:
        company_id = lead.get("external_id")
        log.info(f"Обработка лида: {lead.get('name')} | Телефон: {lead.get('phone')}")
        
        success = await send_to_n8n(lead)
        if success:
            await update_lead_status(company_id, "sent")
            # Имитация задержки человека (от 30с до 2 минут), чтобы не забанили
            await asyncio.sleep(2) # Заглушка, в проде увеличить до 30-120
        else:
            await update_lead_status(company_id, "failed")

if __name__ == "__main__":
    asyncio.run(process_outreach())
