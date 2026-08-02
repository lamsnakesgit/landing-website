import os
import re
import json
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

def extract_contacts(text: str) -> dict:
    """Извлекает контакты (телефон, email, telegram) из текста постов в Telegram"""
    phones = re.findall(r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    tgs = re.findall(r't\.me/([a-zA-Z0-9_]+)|@([a-zA-Z0-9_]{5,})', text)
    
    clean_phone = ""
    if phones:
        raw_p = re.sub(r'\D', '', phones[0])
        if len(raw_p) >= 10:
            clean_phone = '+' + raw_p
            
    clean_email = emails[0] if emails else ""
    
    clean_tg = ""
    if tgs:
        tg_tuple = tgs[0]
        handle = tg_tuple[0] or tg_tuple[1]
        if handle and handle.lower() not in ['joinchat', 'share', 'addstickers', 'proxy']:
            clean_tg = '@' + handle

    clean_wa = f"https://wa.me/{clean_phone.replace('+', '')}" if clean_phone else ""

    return {
        "phone": clean_phone,
        "email": clean_email,
        "telegram": clean_tg,
        "whatsapp": clean_wa
    }

def parse_telegram_chat_leads(keyword: str, max_results: int = 15) -> list:
    """
    Поиск коммерческих запросов в Telegram чатах и каналах (t.me).
    """
    logger.info(f"Telegram Чаты: Поиск коммерческих запросов по ключу '{keyword}'...")
    queries = [
        f'site:t.me "{keyword}" (нужен OR ищу OR требуется OR писать в лс OR contact)',
        f'site:t.me "{keyword}" (разработка OR маркетинг OR отдел продаж)'
    ]
    
    leads = []
    seen_urls = set()
    
    try:
        with DDGS() as ddgs:
            for query in queries:
                results = list(ddgs.text(query, max_results=max_results))
                for res in results:
                    url = res.get('href', '')
                    title = res.get('title', '')
                    snippet = res.get('body', '')
                    
                    if 't.me' not in url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Извлекаем Telegram username из URL
                    handle_match = re.search(r't\.me/([a-zA-Z0-9_]+)', url)
                    tg_handle = f"@{handle_match.group(1)}" if handle_match and handle_match.group(1) not in ['joinchat', 's'] else ""
                    
                    full_text = f"{title} {snippet}"
                    contacts = extract_contacts(full_text)
                    
                    # Заменяем контакт на извлеченный tg_handle если не найден
                    final_tg = contacts["telegram"] or tg_handle
                    
                    leads.append({
                        "source": "Telegram Чаты",
                        "company_name": f"TG {final_tg if final_tg else 'Пользователь'}",
                        "name": final_tg if final_tg else "Заказчик Telegram",
                        "position": "Заказчик / Автор сообщения",
                        "profile_url": url,
                        "snippet": snippet,
                        "title": title,
                        "phone": contacts["phone"],
                        "email": contacts["email"],
                        "telegram": final_tg,
                        "whatsapp": contacts["whatsapp"],
                        "query": keyword,
                        "ai_score": 10 if "нужен" in snippet.lower() or "ищу" in snippet.lower() else 8,
                        "intent_type": "🔥 Запрос в Telegram Чате"
                    })
                    
        logger.info(f"Telegram Чаты: Найдено {len(leads)} лидов по запросу '{keyword}'.")
        return leads
    except Exception as e:
        logger.error(f"Ошибка парсинга Telegram чатов: {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_telegram_chat_leads("ищу маркетолога")
    print(f"Результат Telegram Чаты: {len(res)} лидов")
