import os
import re
import json
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

def extract_contacts_from_text(text: str) -> dict:
    """Извлекает контакты (телефон, email, telegram, whatsapp) из произвольного текста"""
    phones = re.findall(r'(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}', text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    tgs = re.findall(r'(?:t\.me/|@)([a-zA-Z0-9_]{5,32})', text)
    
    clean_phone = ""
    if phones:
        raw_p = re.sub(r'\D', '', phones[0])
        if len(raw_p) == 11:
            if raw_p.startswith('8'):
                raw_p = '7' + raw_p[1:]
            clean_phone = '+' + raw_p
            
    clean_email = emails[0] if emails else ""
    
    clean_tg = ""
    if tgs:
        tg_val = tgs[0]
        if tg_val.lower() not in ['telegram', 'share', 'channel', 'group', 'bot']:
            clean_tg = '@' + tg_val

    clean_wa = f"https://wa.me/{clean_phone.replace('+', '')}" if clean_phone else ""

    return {
        "phone": clean_phone,
        "email": clean_email,
        "telegram": clean_tg,
        "whatsapp": clean_wa
    }

def parse_adata_leads(keyword: str, max_results: int = 15) -> list:
    """
    Поиск компаний и контрагентов на Adata.kz по ключевому слову.
    Возвращает список структурированных карточек лидов.
    """
    logger.info(f"Adata.kz: Начинаю поиск компаний по запросу: '{keyword}'")
    queries = [
        f'site:adata.kz "{keyword}" (телефон OR контакты OR БИН OR ТОО OR ИП OR руководителя)',
        f'site:adata.kz "{keyword}"'
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
                    
                    if 'adata.kz' not in url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Чистим заголовок компании от бренда Adata
                    company_name = title.split('—')[0].split('|')[0].split('- Adata')[0].strip()
                    if not company_name or company_name.lower() in ['adata', 'adata.kz', 'главная']:
                        # Вытаскиваем название из фрагментов текста
                        bin_match = re.search(r'(ТОО|ИП)\s+["«]?[А-Яа-яA-Za-z0-9_\s\-]+["»]?', snippet)
                        company_name = bin_match.group(0) if bin_match else f"Компания Adata ({keyword})"
                        
                    full_text = f"{title} {snippet}"
                    contacts = extract_contacts_from_text(full_text)
                    
                    # Вытаскиваем БИН или руководитель
                    lpr_match = re.search(r'Руководитель:\s*([А-Яа-яA-Za-z\s]+)', snippet)
                    lpr_name = lpr_match.group(1).strip() if lpr_match else "Руководитель компании"
                    
                    leads.append({
                        "source": "adata.kz",
                        "company_name": company_name,
                        "name": lpr_name,
                        "position": "Руководитель / ЛПР",
                        "url": url,
                        "description": f"Профиль на Adata.kz: {snippet}",
                        "phone": contacts["phone"],
                        "email": contacts["email"],
                        "telegram": contacts["telegram"],
                        "whatsapp": contacts["whatsapp"],
                        "query": keyword,
                        "city": "Казахстан",
                        "ai_score": 8 if contacts["phone"] or contacts["telegram"] else 6,
                        "intent_type": "💼 Реестр компании Adata.kz"
                    })
                    
        logger.info(f"Adata.kz: Найдено {len(leads)} лидов по запросу '{keyword}'.")
        return leads
    except Exception as e:
        logger.error(f"Ошибка парсинга Adata.kz: {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_adata_leads("разработка")
    print(f"Результат Adata.kz: найдено {len(res)} лидов")
