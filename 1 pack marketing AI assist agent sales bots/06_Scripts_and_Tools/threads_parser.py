import os
import re
import json
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

def extract_contacts_from_text(text: str) -> dict:
    """Извлекает контакты (телефон, email, telegram, whatsapp) из произвольного текста"""
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

def parse_threads_leads(keyword: str, max_results: int = 15) -> list:
    """
    Поиск профилей и коммерческих постов в Threads.net по ключевому слову.
    Возвращает список структурированных карточек лидов.
    """
    logger.info(f"Threads: Начинаю поиск лидов по запросу: '{keyword}'")
    queries = [
        f'site:threads.net "{keyword}" (email OR whatsapp OR tg OR contact OR dm OR "+7")',
        f'site:threads.net "{keyword}" (нужен OR ищу OR требуется OR разработка)'
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
                    
                    if 'threads.net' not in url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Извлекаем хэндл пользователя Threads
                    handle_match = re.search(r'threads\.net/@([a-zA-Z0-9._]+)', url)
                    handle = f"@{handle_match.group(1)}" if handle_match else "@threads_user"
                    
                    full_text = f"{title} {snippet}"
                    contacts = extract_contacts_from_text(full_text)
                    
                    leads.append({
                        "source": "Threads.net",
                        "company_name": f"Threads {handle}",
                        "name": handle,
                        "position": "Автор поста / Владелец аккаунта",
                        "profile_url": url,
                        "snippet": snippet,
                        "title": title,
                        "phone": contacts["phone"],
                        "email": contacts["email"],
                        "telegram": contacts["telegram"],
                        "whatsapp": contacts["whatsapp"],
                        "query": keyword,
                        "ai_score": 8 if contacts["phone"] or contacts["telegram"] else 6,
                        "intent_type": "💡 Социальный запрос"
                    })
                    
        logger.info(f"Threads: Найдено {len(leads)} лидов по запросу '{keyword}'.")
        return leads
    except Exception as e:
        logger.error(f"Ошибка парсинга Threads: {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_threads_leads("ищу маркетолога")
    print(f"Результат Threads: найдено {len(res)} лидов")
