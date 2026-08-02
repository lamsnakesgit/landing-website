import os
import re
import sys
import json
import time
import requests
from dotenv import load_dotenv
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        DDGS = None
from loguru import logger

load_dotenv()

# Авторизация Vertex AI (Gemini 2.5 Flash)
_vertex_headers = None
_vertex_url = None

def init_vertex_ai():
    global _vertex_headers, _vertex_url
    if _vertex_headers is not None:
        return True
    
    sa_path = "vertex_sa.json"
    if not os.path.exists(sa_path):
        import glob
        sa_files = glob.glob("vertex_sa*.json")
        if sa_files:
            sa_path = sa_files[0]

    if os.path.exists(sa_path):
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            with open(sa_path, "r") as f:
                sa_info = json.load(f)
                project_id = sa_info.get("project_id")
            
            creds = service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            class CustomRequest(Request):
                def __call__(self, *args, **kwargs):
                    kwargs['timeout'] = 15
                    return super().__call__(*args, **kwargs)
            
            creds.refresh(CustomRequest())
            location = "us-central1"
            model_name = "gemini-2.5-flash"
            _vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:generateContent"
            _vertex_headers = {
                "Authorization": f"Bearer {creds.token}",
                "Content-Type": "application/json"
            }
            logger.info("LPR Enricher: Vertex AI успешно инициализирован.")
            return True
        except Exception as e:
            logger.error(f"LPR Enricher: Ошибка инициализации Vertex AI: {e}")
            return False
    return False

def search_duckduckgo(query, max_results=5):
    """Выполняет каскадный поисковый OSINT запрос через DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return "\n".join([f"- {r.get('title', '')}: {r.get('body', '')} [URL: {r.get('href', '')}]" for r in results])
    except Exception as e:
        logger.warning(f"Ошибка DuckDuckGo поиска: {e}")
        return ""

def extract_contacts_from_text(text):
    """Извлекает регулярками телефоны, email, telegram юзернеймы и WhatsApp из сырого текста"""
    phones = re.findall(r'(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}', text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    telegrams = re.findall(r'(?:t\.me/|@)([a-zA-Z0-9_]{5,32})', text)
    whatsapps = re.findall(r'(?:wa\.me/|whatsapp\.com/send\?phone=)(\+?\d{10,15})', text)
    
    # Исключаем служебные файлы и статические расширения из email
    clean_emails = [e for e in set(emails) if not e.endswith(('.png', '.jpg', '.jpeg', '.svg', '.js', '.css'))]
    
    clean_phones = []
    for p in set(phones):
        digits = re.sub(r'\D', '', p)
        if len(digits) == 11:
            if digits.startswith('8'):
                digits = '7' + digits[1:]
            clean_phones.append('+' + digits)
            
    clean_tgs = ['@' + tg if not tg.startswith('@') else tg for tg in set(telegrams) if tg.lower() not in ['telegram', 'share', 'channel', 'group', 'bot']]
    clean_was = ['+' + re.sub(r'\D', '', wa) for wa in set(whatsapps)]
    
    return {
        "phones": clean_phones,
        "emails": clean_emails,
        "telegrams": clean_tgs,
        "whatsapps": clean_was
    }

def enrich_lead_data(company_name, query_niche="", city=""):
    """
    Каскадный OSINT-обогатитель контактов ЛПР и реквизитов компании.
    Сначала собирает данные через DDGS/OSINT, затем анализирует через Vertex AI / Gemini.
    """
    logger.info(f"[*] OSINT-обогащение для: {company_name} ({query_niche}, {city})")
    
    # 1. Формируем каскадные запросы
    q1 = f'"{company_name}" {city} контакты телефон email дирекции отдел продаж site:t.me OR site:wa.me'
    q2 = f'"{company_name}" БИН ИНН генеральный директор контакты'
    
    snippets_1 = search_duckduckgo(q1, max_results=5)
    snippets_2 = search_duckduckgo(q2, max_results=3)
    
    combined_snippets = f"Результаты поиска контактов:\n{snippets_1}\n\nРезультаты поиска по БИН/Директору:\n{snippets_2}"
    
    # Эвристическое извлечение регулярками
    raw_contacts = extract_contacts_from_text(combined_snippets)
    
    # 2. Инициализируем ИИ для глубокого структурирования
    if _vertex_headers is None:
        init_vertex_ai()
        
    system_prompt = (
        "Вы — ведущий OSINT-аналитик по B2B-разведке. Извлеките точную контактную информацию компании и ЛПР "
        "из результатов поискового сниппета.\n"
        "ВАЖНО: Ищите любые реальные телефоны (+7...), WhatsApp ссылки, Telegram хэндлы, E-mail и ФИО директора.\n"
        "Верните результат строго в формате JSON со следующей структурой:\n"
        "{\n"
        '  "lpr_name": "ФИО или null",\n'
        '  "position": "Генеральный директор / Маркетолог / HRD / Руководитель или null",\n'
        '  "phone": "Телефон в формате +7XXXXXXXXXX или null",\n'
        '  "whatsapp": "Ссылка https://wa.me/7... или null",\n'
        '  "telegram": "@username или ссылка t.me/... или null",\n'
        '  "email": "email@domain.com или null",\n'
        '  "website": "https://... или null",\n'
        '  "inn_bin": "ИНН/БИН или null",\n'
        '  "has_valid_contact": true/false\n'
        "}"
    )
    
    user_prompt = (
        f"Компания: {company_name}\n"
        f"Ниша/Город: {query_niche} ({city})\n"
        f"Сырые найденные контакты: {json.dumps(raw_contacts, ensure_ascii=False)}\n\n"
        f"Сниппеты поиска:\n{combined_snippets}\n"
    )
    
    result_data = {
        "company_name": company_name,
        "lpr_name": None,
        "position": None,
        "phone": raw_contacts['phones'][0] if raw_contacts['phones'] else None,
        "whatsapp": raw_contacts['whatsapps'][0] if raw_contacts['whatsapps'] else (f"https://wa.me/{raw_contacts['phones'][0][1:]}" if raw_contacts['phones'] else None),
        "telegram": raw_contacts['telegrams'][0] if raw_contacts['telegrams'] else None,
        "email": raw_contacts['emails'][0] if raw_contacts['emails'] else None,
        "website": None,
        "inn_bin": None,
        "has_valid_contact": bool(raw_contacts['phones'] or raw_contacts['telegrams'] or raw_contacts['emails'])
    }
    
    if _vertex_headers and _vertex_url:
        try:
            body = {
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(_vertex_url, json=body, headers=_vertex_headers, timeout=20)
            if res.status_code == 200:
                res_json = res.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                clean_text = text.strip().removeprefix("```json").removesuffix("```").strip()
                ai_dict = json.loads(clean_text)
                
                # Обновляем поля, сохраняя извлеченные регулярками, если ИИ вернул null
                for k in ["lpr_name", "position", "phone", "whatsapp", "telegram", "email", "website", "inn_bin"]:
                    if ai_dict.get(k):
                        result_data[k] = ai_dict[k]
                        
                result_data["has_valid_contact"] = bool(
                    result_data.get("phone") or result_data.get("whatsapp") or result_data.get("telegram") or result_data.get("email")
                )
        except Exception as e:
            logger.warning(f"Ошибка ИИ-структурирования в lpr_enricher: {e}")

    return json.dumps(result_data, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    test_company = "ТОО Астана Авто" if len(sys.argv) <= 1 else sys.argv[1]
    res = enrich_lead_data(test_company, "разработка", "Астана")
    print("\n--- Результат OSINT-обогащения ---")
    print(res)
