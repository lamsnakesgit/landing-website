import os
import re
import json
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

def extract_contacts(text: str) -> dict:
    """Извлекает контакты из LinkedIn сниппета или био профиля"""
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
        clean_tg = '@' + (tg_tuple[0] or tg_tuple[1])

    clean_wa = f"https://wa.me/{clean_phone.replace('+', '')}" if clean_phone else ""

    return {
        "phone": clean_phone,
        "email": clean_email,
        "telegram": clean_tg,
        "whatsapp": clean_wa
    }

def parse_linkedin_leads(keyword: str, max_results: int = 15) -> list:
    """
    Выполняет X-ray поиск B2B профилей ЛПР и постов в LinkedIn (Казахстан / СНГ / Глобал).
    """
    logger.info(f"LinkedIn: Поиск B2B ЛПР по запросу '{keyword}'...")
    queries = [
        f'site:linkedin.com/in ("CEO" OR "Founder" OR "Директор" OR "CMO" OR "Head of Sales") "{keyword}" (Казахстан OR Алматы OR Астана OR СНГ)',
        f'site:linkedin.com/posts "{keyword}" (нужен OR ищу OR требуется OR contact OR email)'
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
                    
                    if 'linkedin.com' not in url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Очищаем заголовок профиля (Имя | Должность | Компания)
                    clean_title = re.sub(r'\s*\|\s*LinkedIn.*$', '', title)
                    parts = clean_title.split('-')
                    name = parts[0].strip() if len(parts) > 0 else "B2B ЛПР LinkedIn"
                    position = parts[1].strip() if len(parts) > 1 else "Руководитель / Founder"
                    
                    full_text = f"{title} {snippet}"
                    contacts = extract_contacts(full_text)
                    
                    leads.append({
                        "source": "LinkedIn B2B",
                        "company_name": name,
                        "name": name,
                        "position": position,
                        "profile_url": url,
                        "snippet": snippet,
                        "title": title,
                        "phone": contacts["phone"],
                        "email": contacts["email"],
                        "telegram": contacts["telegram"],
                        "whatsapp": contacts["whatsapp"],
                        "query": keyword,
                        "ai_score": 9 if contacts["email"] or contacts["phone"] else 8,
                        "intent_type": "💼 B2B ЛПР (LinkedIn)"
                    })
                    
        logger.info(f"LinkedIn: Найдено {len(leads)} лидов по запросу '{keyword}'.")
        return leads
    except Exception as e:
        logger.error(f"Ошибка парсинга LinkedIn: {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_linkedin_leads("разработка ботов")
    print(f"Результат LinkedIn: {len(res)} лидов")
