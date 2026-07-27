import os
import re
import json
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def extract_contacts(text: str) -> dict:
    """Извлекает контакты из био профиля или текста твита"""
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

def parse_twitter_x_leads(keyword: str, max_results: int = 15) -> list:
    """
    Выполняет X-ray поиск commercial intent постов и профилей в X (Twitter).
    """
    logger.info(f"X/Twitter: Поиск коммерческих запросов по ключу '{keyword}'...")
    queries = [
        f'(site:x.com OR site:twitter.com) "{keyword}" (нужен OR ищу OR требуется OR contact OR DM)',
        f'(site:x.com OR site:twitter.com) "{keyword}" (email OR whatsapp OR "+7")'
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
                    
                    if not ('x.com' in url or 'twitter.com' in url) or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Извлекаем @username из URL (например twitter.com/username/status/...)
                    handle_match = re.search(r'(?:x\.com|twitter\.com)/([a-zA-Z0-9_]+)', url)
                    handle = f"@{handle_match.group(1)}" if handle_match and handle_match.group(1) not in ['status', 'search', 'intent', 'i'] else "@x_user"
                    
                    full_text = f"{title} {snippet}"
                    contacts = extract_contacts(full_text)
                    
                    leads.append({
                        "source": "X (Twitter)",
                        "company_name": f"X {handle}",
                        "name": handle,
                        "position": "Автор твита / Руководитель",
                        "profile_url": url,
                        "snippet": snippet,
                        "title": title,
                        "phone": contacts["phone"],
                        "email": contacts["email"],
                        "telegram": contacts["telegram"],
                        "whatsapp": contacts["whatsapp"],
                        "query": keyword,
                        "ai_score": 9 if "ищу" in snippet.lower() or "нужен" in snippet.lower() else 7,
                        "intent_type": "🔥 Горячий запрос в X"
                    })
                    
        logger.info(f"X/Twitter: Найдено {len(leads)} лидов по запросу '{keyword}'.")
        return leads
    except Exception as e:
        logger.error(f"Ошибка парсинга X (Twitter): {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_twitter_x_leads("нужен бот")
    print(f"Результат X/Twitter: {len(res)} лидов")
