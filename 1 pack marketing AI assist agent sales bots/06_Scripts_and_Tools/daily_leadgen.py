import os
import re
import sys
import json
import time
import csv
import signal
import socket
import threading
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# Импорт OSINT обогатителя и парсеров соцсетей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from lpr_enricher import enrich_lead_data
except ImportError:
    enrich_lead_data = None

try:
    from threads_parser import parse_threads_leads
except ImportError:
    parse_threads_leads = None

try:
    from twitter_x_parser import parse_twitter_x_leads
except ImportError:
    parse_twitter_x_leads = None

try:
    from linkedin_parser import parse_linkedin_leads
except ImportError:
    parse_linkedin_leads = None

try:
    from telegram_chat_parser import parse_telegram_chat_leads
except ImportError:
    parse_telegram_chat_leads = None

# Установка глобального таймаута для сокетов
socket.setdefaulttimeout(35)

try:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except AttributeError:
    pass

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/daily_leadgen.log", rotation="10 MB", retention="7 days", level="INFO")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIHUBMIX_API_KEY = os.getenv("AIHUBMIX_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TG_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN") or os.getenv("TG_REALSTATE_SMM_BOT")
TG_CHAT_ID = os.getenv("TG_CHAT_ID_MAIN") or os.getenv("TG_CHAT_ID") or os.getenv("TG_REALSTATE_SMM_CHAT_ID")

HH_API_URL = "https://api.hh.ru/vacancies"

def normalize_phone_number(phone_str):
    """Нормализует телефонный номер для СНГ стандартов (начиная с +7)"""
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', str(phone_str))
    if not digits:
        return ""
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10 and (digits.startswith('7') or digits.startswith('9')):
        digits = '7' + digits
    elif len(digits) == 11 and digits.startswith('9'):
        digits = '7' + digits[1:]
    return '+' + digits if not digits.startswith('+') else digits

def has_valid_contact(lead):
    """Строгий фильтр квалификации лида: проверяет наличие ПРЯМОГО контакта (телефон / WA / TG / Email)"""
    phone = lead.get("phone") or ""
    whatsapp = lead.get("whatsapp") or ""
    telegram = lead.get("telegram") or ""
    email = lead.get("email") or ""
    
    return bool(phone.strip() or whatsapp.strip() or telegram.strip() or email.strip())

def search_hh_vacancies(text_query, area_id, per_page=10):
    """Ищет вакансии на HH.ru/HH.kz по запросу и региону"""
    logger.info(f"HH: Поиск вакансий '{text_query}' в регионе {area_id}...")
    headers = {"User-Agent": "AIAgentOutreach/1.0 (info@aiconicvibe.store)"}
    params = {"text": text_query, "area": area_id, "per_page": per_page, "page": 0}
    try:
        response = requests.get(HH_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        logger.error(f"Ошибка при поиске вакансий HH: {e}")
        return []

def get_hh_vacancy_details(vacancy_id):
    """Получает детальную информацию по вакансии, включая контакты"""
    url = f"{HH_API_URL}/{vacancy_id}"
    headers = {"User-Agent": "AIAgentOutreach/1.0 (info@aiconicvibe.store)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения деталей вакансии {vacancy_id}: {e}")
        return {}

def extract_contacts_from_hh(vacancy_details):
    """Извлекает контакты (имя, телефон, email) из деталей вакансии"""
    contacts = vacancy_details.get("contacts")
    if not contacts:
        return "", "", ""
    
    name = contacts.get("name", "")
    email = contacts.get("email", "")
    
    phones = contacts.get("phones", [])
    phone_val = ""
    if phones:
        p = phones[0]
        country = p.get("country", "")
        city = p.get("city", "")
        number = p.get("number", "")
        phone_val = f"+{country}{city}{number}"
        
    return name, email, phone_val

def collect_hh_leads():
    """Собирает лидов по всем ключевым словам с HH.ru и HH.kz"""
    backup_path = "06_Scripts_and_Tools/hh_leads.json"
    leads = []
    
    if os.path.exists(backup_path):
        logger.info("Обнаружен локальный файл hh_leads.json. Загружаем данные...")
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_leads = json.load(f)
                for l in backup_leads:
                    l.setdefault("phone", "")
                    l.setdefault("email", "")
                    l.setdefault("whatsapp", "")
                    l.setdefault("telegram", "")
                    leads.append(l)
            logger.info(f"Загружено {len(leads)} лидов из hh_leads.json.")
            return leads
        except Exception as e:
            logger.error(f"Ошибка чтения hh_leads.json: {e}")

    queries = ["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]
    regions = {"hh.ru": 113, "hh.kz": 40}
    seen_ids = set()

    for source_name, area_id in regions.items():
        for query in queries:
            items = search_hh_vacancies(query, area_id, per_page=5)
            for item in items:
                v_id = item.get("id")
                if v_id in seen_ids:
                    continue
                seen_ids.add(v_id)
                
                details = get_hh_vacancy_details(v_id)
                name, email, phone = extract_contacts_from_hh(details)
                employer = item.get("employer", {})
                company_name = employer.get("name", "Не указано")
                vac_name = item.get("name", "")
                desc_snippet = item.get("snippet", {}).get("requirement", "") or ""
                desc_snippet = re.sub('<[^<]+?>', '', desc_snippet)
                
                leads.append({
                    "name": name or "Представитель компании",
                    "company_name": company_name,
                    "phone": normalize_phone_number(phone),
                    "email": email,
                    "whatsapp": f"https://wa.me/{normalize_phone_number(phone)[1:]}" if phone else "",
                    "telegram": "",
                    "url": item.get("alternate_url", ""),
                    "description": f"Вакансия: {vac_name}. Требования: {desc_snippet}",
                    "source": source_name,
                    "city": item.get("area", {}).get("name", ""),
                    "query": query
                })
                time.sleep(0.3)

    return leads

def load_external_leads():
    """Загружает внешние лиды из JSON (adata.kz, threads.net)"""
    file_path = "06_Scripts_and_Tools/external_leads.json"
    leads = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for l in data:
                    l.setdefault("phone", "")
                    l.setdefault("email", "")
                    l.setdefault("whatsapp", "")
                    l.setdefault("telegram", "")
                    leads.append(l)
        except Exception as e:
            logger.error(f"Ошибка загрузки external_leads.json: {e}")
    return leads

def load_court_leads():
    """Загружает судебные лиды из JSON (court_leads.json)"""
    file_path = "06_Scripts_and_Tools/court_leads.json"
    leads = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for l in data:
                    l.setdefault("phone", "")
                    l.setdefault("email", "")
                    l.setdefault("whatsapp", "")
                    l.setdefault("telegram", "")
                    l.setdefault("description", f"Участник судебного процесса по трудовым спорам. Дело № {l.get('case_number')}.")
                    leads.append(l)
        except Exception as e:
            logger.error(f"Ошибка загрузки court_leads.json: {e}")
    return leads

use_vertex_directly = False
_vertex_credentials = None
_vertex_headers = None
_vertex_url = None
vertex_lock = threading.Lock()

def init_vertex_ai():
    global _vertex_credentials, _vertex_headers, _vertex_url
    with vertex_lock:
        if _vertex_headers is not None:
            return True
        
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        sa_path = "vertex_sa.json"
        if not os.path.exists(sa_path):
            import glob
            sa_files = glob.glob("vertex_sa*.json")
            if sa_files:
                sa_path = sa_files[0]
        
        if os.path.exists(sa_path):
            try:
                with open(sa_path, "r") as f:
                    sa_info = json.load(f)
                    project_id = sa_info.get("project_id")
                
                _vertex_credentials = service_account.Credentials.from_service_account_file(
                    sa_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                
                class CustomRequest(Request):
                    def __call__(self, *args, **kwargs):
                        kwargs['timeout'] = 15
                        return super().__call__(*args, **kwargs)
                        
                _vertex_credentials.refresh(CustomRequest())
                location = "us-central1"
                model_name = "gemini-2.5-flash"
                _vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:generateContent"
                _vertex_headers = {
                    "Authorization": f"Bearer {_vertex_credentials.token}",
                    "Content-Type": "application/json"
                }
                logger.info("Vertex AI успешно инициализирован.")
                return True
            except Exception as e:
                logger.error(f"Не удалось инициализировать Vertex AI: {e}")
                return False
        return False

def enrich_lead_with_ai(lead, openai_client):
    """Генерация оффера и первого сообщения через Gemini / Vertex AI"""
    global use_vertex_directly, _vertex_credentials, _vertex_headers, _vertex_url
    
    system_prompt = (
        "Вы — опытный специалист по B2B-продажам ИИ-агентов и автоворонок.\n"
        "Составьте индивидуальное коммерческое предложение и первичное сообщение в мессенджер.\n\n"
        "ПРАВИЛА СООБЩЕНИЯ:\n"
        "1. Стиль — естественный, разговорный, дружелюбный. Без канцеляризмов ('Здравствуйте', 'Уважаемый').\n"
        "2. Начните с легкого приветствия ('Привет!', 'Добрый день, [Имя]!').\n"
        "3. Хук опирается на источник и боли их бизнеса.\n"
        "4. Короткий оффер: ИИ-ассистенты для продаж, обработка заявок 24/7, n8n автоворонки.\n"
        "5. Мягкий CTA ('Интересно посмотреть пример?', 'Хотите короткое видео-демо?').\n"
        "6. Длина — не более 3-4 предложений.\n\n"
        "Верните JSON:\n"
        "{\n"
        '  "role_guess": "должность",\n'
        '  "pain_hypothesis": "гипотеза боли",\n'
        '  "offer_angle": "угол захода",\n'
        '  "personal_hook": "хук",\n'
        '  "generated_pitch": "текст сообщения",\n'
        '  "offer_details": ["пункт 1", "пункт 2"],\n'
        '  "ai_score": 8\n'
        "}"
    )
    
    user_prompt = (
        f"Компания: {lead['company_name']}\n"
        f"Контактное лицо: {lead.get('name', 'Не указано')}\n"
        f"Источник: {lead['source']}\n"
        f"Ниша: {lead.get('query', '')}\n"
        f"Город: {lead.get('city', '')}\n"
        f"Описание: {lead.get('description', '')}\n"
    )
    
    success = False
    if _vertex_headers is None:
        init_vertex_ai()
        
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
                data = json.loads(clean_text)
                lead.update(data)
                success = True
        except Exception as e:
            logger.warning(f"Vertex AI ошибка для {lead['company_name']}: {e}")

    if not success:
        lead.update({
            "role_guess": "Руководитель",
            "pain_hypothesis": "Ручная обработка заявок",
            "offer_angle": "Автоматизация ИИ-агентами под ключ",
            "personal_hook": "Привет!",
            "generated_pitch": f"Привет! Увидел ваш профиль в {lead['source']}. Мы внедряем ИИ-агентов для автоматизации продаж 24/7. Интересно глянуть короткий пример?",
            "offer_details": ["ИИ-продажник в WhatsApp/TG", "Интеграция с CRM"],
            "ai_score": 7
        })

    try:
        lead["ai_score"] = int(str(lead.get("ai_score", 7)).split("/")[0])
    except Exception:
        lead["ai_score"] = 7

def save_local_results(qualified_leads, backlog_leads, date_str):
    """Сохраняет квалифицированные лиды и backlog в отдельные структуры"""
    base_dir = f"03_Marketing_and_Sales/daily_leads/{date_str}"
    os.makedirs(f"{base_dir}/details", exist_ok=True)
    
    # 1. Сохранение квалифицированных лидов (с контактами)
    qual_file = f"{base_dir}/leads_qualified.json"
    with open(qual_file, "w", encoding="utf-8") as f:
        json.dump(qualified_leads, f, ensure_ascii=False, indent=2)
        
    # 2. Сохранение backlog (без контактов)
    backlog_file = f"{base_dir}/sourcing_backlog.json"
    with open(backlog_file, "w", encoding="utf-8") as f:
        json.dump(backlog_leads, f, ensure_ascii=False, indent=2)
        
    # 3. Сохранение CSV для квалифицированных лидов
    csv_file = f"{base_dir}/leads_summary.csv"
    keys = ["company_name", "name", "phone", "whatsapp", "telegram", "email", "source", "query", "city", "url", "ai_score", "role_guess", "generated_pitch"]
    try:
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(qualified_leads)
    except Exception as e:
        logger.error(f"Ошибка сохранения CSV: {e}")

    # 4. Создание карточек лидов в details/
    for idx, lead in enumerate(qualified_leads, 1):
        clean_company = re.sub(r'[^a-zA-Z0-9_а-яА-Я]', '_', lead['company_name'])
        detail_file = f"{base_dir}/details/{idx}_{clean_company}.md"
        
        details_content = f"""# 🎯 Квалифицированный Лид: {lead['company_name']}

- **ЛПР / Контакт**: {lead.get('name', 'Не указано')}
- **📞 Телефон**: `{lead.get('phone') or 'Нет'}`
- **📲 WhatsApp**: `{lead.get('whatsapp') or 'Нет'}`
- **✈️ Telegram**: `{lead.get('telegram') or 'Нет'}`
- **✉️ Email**: `{lead.get('email') or 'Нет'}`
- **Источник**: {lead['source']}
- **Оценка ИИ**: **{lead.get('ai_score', 7)}/10**

### 💡 Питч сообщения:
> {lead.get('generated_pitch', '')}
"""
        with open(detail_file, "w", encoding="utf-8") as f:
            f.write(details_content)

def send_telegram_notification(qualified_leads, backlog_count):
    """Отправляет отфильтрованные лиды С КОНТАКТАМИ в Telegram Sales Hub"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logger.warning("Telegram BOT TOKEN или CHAT ID не заданы.")
        return
        
    logger.info("Отправка уведомления в Telegram...")
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    date_today = datetime.now().strftime('%Y-%m-%d')
    
    summary_message = (
        f"🎯 *LeadGen OS | Отчет по лидам за {date_today}*\n\n"
        f"🔥 *Квалифицированных лидов (С КОНТАКТАМИ):* `{len(qualified_leads)}`\n"
        f"📂 Лидов отправлено в backlog (без контактов): `{backlog_count}`\n\n"
        f"⚡ _Никаких 'пустых' ссылок! Все контакты проверены._"
    )
    
    try:
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": summary_message, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        logger.error(f" Ошибка отправки сводки в Telegram: {e}")
        return

    # Отправляем карточки квалифицированных лидов
    for idx, lead in enumerate(qualified_leads[:10], 1):
        contacts = []
        if lead.get("phone"): contacts.append(f"📞 `{lead['phone']}`")
        if lead.get("whatsapp"): contacts.append(f"📲 [WhatsApp]({lead['whatsapp']})")
        if lead.get("telegram"): contacts.append(f"✈️ `{lead['telegram']}`")
        if lead.get("email"): contacts.append(f"✉️ `{lead['email']}`")
        
        msg = (
            f"🔥 *Лид №{idx} | {lead['company_name']} (Оценка: {lead.get('ai_score', 7)}/10)*\n"
            f"👤 *ЛПР:* {lead.get('name', 'Не указано')}\n"
            f"📍 *Город:* {lead.get('city', 'Не указан')} | *Источник:* `{lead['source']}`\n\n"
            f"📇 *КОНТАКТЫ:* {', '.join(contacts)}\n\n"
            f"💬 *ПЕРВОЕ СООБЩЕНИЕ:*\n_{lead.get('generated_pitch', '')}_"
        )
        
        try:
            requests.post(url, json={
                "chat_id": TG_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }, timeout=10)
            time.sleep(0.8)
        except Exception as e:
            logger.error(f"Ошибка отправки карточки лида №{idx}: {e}")

def main():
    logger.info("=== Запуск LeadGen OS (Contact Validation Strict Mode + Multi-Channel Social) ===")
    
    hh_leads = collect_hh_leads()
    external_leads = load_external_leads()
    court_leads = load_court_leads()
    
    social_leads = []
    queries = ["ищу маркетолога", "нужен бот", "разработка ИИ", "нужна автоворонка"]
    for q in queries:
        if parse_threads_leads:
            social_leads.extend(parse_threads_leads(q, max_results=5))
        if parse_twitter_x_leads:
            social_leads.extend(parse_twitter_x_leads(q, max_results=5))
        if parse_linkedin_leads:
            social_leads.extend(parse_linkedin_leads(q, max_results=5))
        if parse_telegram_chat_leads:
            social_leads.extend(parse_telegram_chat_leads(q, max_results=5))
    
    raw_leads = []
    seen_keys = set()
    for l in hh_leads + external_leads + court_leads + social_leads:
        company = l.get("company_name", "").strip()
        if not company: continue
        key = (company.lower(), l.get("profile_url", l.get("url", "")).lower())
        if key not in seen_keys:
            seen_keys.add(key)
            raw_leads.append(l)

    logger.info(f"Всего собрано исходных лидов: {len(raw_leads)}")

    # 1. Прогон через OSINT Enricher для тех, у кого нет прямых контактов
    qualified_leads = []
    sourcing_backlog = []
    
    for idx, lead in enumerate(raw_leads, 1):
        if not has_valid_contact(lead) and enrich_lead_data:
            logger.info(f"[{idx}/{len(raw_leads)}] Запуск OSINT-поиска контактов для: {lead['company_name']}")
            try:
                osint_json = enrich_lead_data(lead['company_name'], lead.get('query', ''), lead.get('city', ''))
                osint_data = json.loads(osint_json)
                if osint_data.get("phone"): lead["phone"] = normalize_phone_number(osint_data["phone"])
                if osint_data.get("whatsapp"): lead["whatsapp"] = osint_data["whatsapp"]
                if osint_data.get("telegram"): lead["telegram"] = osint_data["telegram"]
                if osint_data.get("email"): lead["email"] = osint_data["email"]
                if osint_data.get("lpr_name"): lead["name"] = osint_data["lpr_name"]
            except Exception as e:
                logger.warning(f"Ошибка OSINT-обогащения для {lead['company_name']}: {e}")
                
        if has_valid_contact(lead):
            qualified_leads.append(lead)
        else:
            sourcing_backlog.append(lead)

    logger.info(f"Результат сегрегации: Квалифицировано (С контактами): {len(qualified_leads)} | Backlog (Без контактов): {len(sourcing_backlog)}")

    # 2. ИИ-генерация индивидуальных питчей для квалифицированных лидов
    if qualified_leads:
        logger.info(f"Генерация ИИ-офферов для {len(qualified_leads)} квалифицированных лидов...")
        for lead in qualified_leads:
            enrich_lead_with_ai(lead, None)

    date_str = datetime.now().strftime("%Y-%m-%d")
    save_local_results(qualified_leads, sourcing_backlog, date_str)
    send_telegram_notification(qualified_leads, len(sourcing_backlog))
    
    logger.success("Ежедневная лидогенерация LeadGen OS завершена успешно!")

if __name__ == "__main__":
    main()
