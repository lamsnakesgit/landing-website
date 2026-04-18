import requests
import json
from loguru import logger

# Настройка под твой VPS Evolution API
EVOLUTION_BASE_URL = "https://evolutionapi.aiconicvibe.store"
API_KEY = "ТВОЙ_GLOBAL_API_KEY_ЗДЕСЬ"  # Замени на реальный ключ

def check_instances():
    """Проверяет запущенные инстансы (номера WhatsApp)"""
    url = f"{EVOLUTION_BASE_URL}/instance/fetchInstances"
    headers = {
        "apikey": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            logger.error("Ошибка 403: Неверный API ключ или блок от Cloudflare.")
            return []
            
        data = response.json()
        logger.info(f"Найдено инстансов: {len(data)}")
        
        for inst in data:
            inst_name = inst.get("instance", {}).get("instanceName")
            status = inst.get("instance", {}).get("status")
            logger.info(f"Инстанс: {inst_name} | Статус: {status}")
            
        return data
    except Exception as e:
        logger.error(f"Ошибка соединения с Evolution API: {e}")
        return []

def send_test_message(instance_name, target_number, text):
    """Отправляет тестовое сообщение через указанный инстанс"""
    url = f"{EVOLUTION_BASE_URL}/message/sendText/{instance_name}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": target_number,
        "options": {
            "delay": 1200,      # Задержка 1.2 сек, чтобы имитировать печать
            "presence": "composing", 
            "linkPreview": False
        },
        "textMessage": {
            "text": text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            logger.success(f"Сообщение успешно отправлено на {target_number}")
            return response.json()
        else:
            logger.error(f"Ошибка от Evolution API: {response.text}")
    except Exception as e:
        logger.error(f"Сбой отправки сообщения: {e}")

if __name__ == "__main__":
    logger.info("--- Тест Инфраструктуры Evolution API ---")
    instances = check_instances()
    
    # Если хочешь отправить сообщения, раскомментируй ниже и вставь свой номер
    # if instances:
    #     first_instance = instances[0].get("instance", {}).get("instanceName")
    #     send_test_message(first_instance, "77001234567", "Привет! Это серверная проверка AI-агента. Как слышно?")
