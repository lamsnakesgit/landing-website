import os
import re
import sys
import json
import time
import csv
import signal
import socket
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import requests
from openai import OpenAI

# Установка глобального таймаута для всех сокетов
socket.setdefaulttimeout(35)

# Игнорируем SIGHUP сигнал для надежности при работе в сессиях launchd/Terminal
try:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except AttributeError:
    pass

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/daily_leadgen.log", rotation="10 MB", retention="7 days", level="INFO")

# Загрузка переменных окружения
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIHUBMIX_API_KEY = os.getenv("AIHUBMIX_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TG_BOT_TOKEN = os.getenv("TG_REALSTATE_SMM_BOT")
# Используем TG_CHAT_ID, а в качестве резерва TG_REALSTATE_SMM_CHAT_ID или TG_CHAT_ID_MAIN
TG_CHAT_ID = os.getenv("TG_CHAT_ID") or os.getenv("TG_REALSTATE_SMM_CHAT_ID") or os.getenv("TG_CHAT_ID_MAIN")

HH_API_URL = "https://api.hh.ru/vacancies"

def normalize_phone_number(phone_str):
    """Нормализует телефонный номер для СНГ стандартов (начиная с 7)"""
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', phone_str)
    if not digits:
        return ""
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10 and (digits.startswith('7') or digits.startswith('9')):
        digits = '7' + digits
    elif len(digits) == 11 and digits.startswith('9'):
        digits = '7' + digits[1:]
    return digits

def search_hh_vacancies(text_query, area_id, per_page=10):
    """Ищет вакансии на HH.ru/HH.kz по запросу и региону"""
    logger.info(f"HH: Поиск вакансий '{text_query}' в регионе {area_id}...")
    headers = {"User-Agent": "AIAgentOutreach/1.0 (info@aiconicvibe.store)"}
    params = {
        "text": text_query,
        "area": area_id,
        "per_page": per_page,
        "page": 0
    }
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
        phone_val = f"+{country} ({city}) {number}"
        
    return name, email, phone_val

def collect_hh_leads():
    """Собирает лидов по всем ключевым словам с HH.ru и HH.kz. С решением при 403."""
    backup_path = "06_Scripts_and_Tools/hh_leads.json"
    leads = []
    
    # Сначала проверяем наличие свежего файла от Playwright-скрапера
    if os.path.exists(backup_path):
        logger.info("Обнаружен локальный файл hh_leads.json от Playwright-скрапера. Загружаем данные напрямую для стабильности...")
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_leads = json.load(f)
                for l in backup_leads:
                    l.setdefault("phone", "")
                    l.setdefault("email", "")
                    leads.append(l)
            logger.info(f"Успешно загружено {len(leads)} лидов из hh_leads.json.")
            return leads
        except Exception as e:
            logger.error(f"Не удалось прочитать hh_leads.json: {e}. Переходим к запасному API сбору...")
            leads = []

    queries = ["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]
    regions = {"hh.ru": 113, "hh.kz": 40}
    seen_ids = set()
    api_blocked = False

    for source_name, area_id in regions.items():
        for query in queries:
            logger.info(f"Запуск сбора по API: {source_name}, запрос: {query}")
            items = search_hh_vacancies(query, area_id, per_page=5)
            if not items:
                api_blocked = True
                continue
                
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
                    "phone": phone,
                    "email": email,
                    "url": item.get("alternate_url", ""),
                    "description": f"Вакансия: {vac_name}. Требования: {desc_snippet}",
                    "source": source_name,
                    "city": item.get("area", {}).get("name", ""),
                    "query": query
                })
                time.sleep(0.5)

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
                    l.setdefault("description", f"Участник судебного процесса по трудовым спорам. Дело № {l.get('case_number')}. Результат: {l.get('court_result')}")
                    leads.append(l)
        except Exception as e:
            logger.error(f"Ошибка загрузки court_leads.json: {e}")
    return leads

use_vertex_directly = False
_vertex_credentials = None
_vertex_headers = None
_vertex_url = None

def enrich_lead_with_ai(lead, openai_client):
    """Использует OpenAI для генерации персонализированного оффера и сообщения с автоматическим фоллбэком на Vertex AI"""
    global use_vertex_directly, _vertex_credentials, _vertex_headers, _vertex_url
    logger.info(f"ИИ-анализ для лида: {lead['company_name']} ({lead['source']})")
    
    system_prompt = (
        "Вы — опытный специалист по B2B-продажам и AI-ассистентам.\n"
        "Проанализируйте информацию о лиде и составьте индивидуальное коммерческое предложение "
        "и текст первого сообщения для связи в мессенджере (в стиле Ника Сараева).\n\n"
        "ПРАВИЛА НАПИСАНИЯ СООБЩЕНИЯ:\n"
        "1. Стиль — разговорный, дружелюбный, простой русский язык. Без официоза и канцеляризмов (не пишите 'Здравствуйте!', 'Уважаемый', 'Надеемся на сотрудничество').\n"
        "2. Вместо этого начните с легкого приветствия: 'Привет!', 'Добрый день, [Имя]!' (если имя неизвестно, то просто 'Привет!' или 'Добрый день!')\n"
        "3. Хук должен ссылаться на контекст (где нашли: HH вакансия, adata.kz, threads profile) и показывать понимание их специфики.\n"
        "4. Предложите конкретное решение боли: создание чат-ботов, ИИ-ассистентов для ответов клиентам, автоматизацию CRM с помощью n8n, контекстную рекламу или генерацию ИИ-контента.\n"
        "5. Призыв к действию (CTA) должен быть мягким, без навязывания (например, 'Интересно глянуть пример?', 'Хотите скину короткое видео-демо?').\n"
        "6. Длина сообщения — до 3-4 предложений.\n\n"
        "Верните результат строго в формате JSON с ключами:\n"
        "- role_guess: предположение о должности контакта (например, HR, CEO, Маркетолог)\n"
        "- pain_hypothesis: гипотеза о боли бизнеса (в чем их проблема/потребность)\n"
        "- offer_angle: под каким углом заходить с предложением\n"
        "- personal_hook: индивидуальный хук для начала беседы\n"
        "- generated_pitch: текст первого сообщения\n"
        "- offer_details: что конкретно мы можем им предложить (список из 2-3 пунктов)\n"
        "- ai_score: оценка соответствия от 1 до 10\n"
    )
    
    user_prompt = (
        f"Компания: {lead['company_name']}\n"
        f"Контактное лицо: {lead['name']}\n"
        f"Источник: {lead['source']}\n"
        f"Ниша/Тема: {lead['query']}\n"
        f"Город: {lead.get('city', '')}\n"
        f"Описание: {lead['description']}\n"
    )
    
    success = False
    if openai_client and not use_vertex_directly:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                timeout=30
            )
            data = json.loads(response.choices[0].message.content)
            lead.update(data)
            success = True
        except Exception as e:
            logger.error(f"Ошибка OpenAI для лида {lead['company_name']}: {e}. Пробуем фоллбэк на Vertex AI (Gemini 2.5 Flash)...")
            err_msg = str(e).lower()
            if "insufficient" in err_msg or "quota" in err_msg or "403" in err_msg or "balance" in err_msg:
                use_vertex_directly = True
                logger.warning("⚠️ Квота OpenAI/AIHubMix исчерпана или доступ запрещен. Переключаемся на Vertex AI напрямую для всех оставшихся лидов.")
                
    if not success:
        try:
            if _vertex_headers is None:
                from google.oauth2 import service_account
                from google.auth.transport.requests import Request
                
                sa_path = "vertex_sa.json"
                if not os.path.exists(sa_path):
                    import glob
                    sa_files = glob.glob("vertex_sa*.json")
                    if sa_files:
                        sa_path = sa_files[0]
                        logger.info(f"Файл vertex_sa.json не найден, используем найденный по маске: {sa_path}")
                
                if os.path.exists(sa_path):
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
                            
                    logger.info("Обновляем токен доступа Google Cloud OAuth2...")
                    _vertex_credentials.refresh(CustomRequest())
                    
                    location = "us-central1"
                    model_name = "gemini-2.5-flash"
                    _vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:generateContent"
                    
                    _vertex_headers = {
                        "Authorization": f"Bearer {_vertex_credentials.token}",
                        "Content-Type": "application/json"
                    }
                    logger.info("Авторизация Vertex AI успешно инициализирована и кэширована.")
                else:
                    raise FileNotFoundError("Файл vertex_sa.json не найден")
            
            body = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }],
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            
            for attempt in range(3):
                try:
                    logger.info(f"Запрос Vertex AI HTTP для {lead['company_name']}, попытка {attempt+1}...")
                    res = requests.post(_vertex_url, json=body, headers=_vertex_headers, timeout=25)
                    res.raise_for_status()
                    
                    res_json = res.json()
                    text = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    # Очистка текста от Markdown-блоков json
                    clean_text = text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    clean_text = clean_text.strip()
                    
                    data = json.loads(clean_text)
                    lead.update(data)
                    success = True
                    logger.info(f"Успешно обогащено через Vertex AI (Gemini 2.5 Flash по HTTP) для {lead['company_name']}")
                    break
                except Exception as exc:
                    if attempt < 2:
                        wait_time = (attempt + 1) * 3
                        logger.warning(f"Попытка {attempt+1} обогащения через Vertex AI HTTP для {lead['company_name']} завершилась ошибкой: {exc}. Ждем {wait_time} сек...")
                        time.sleep(wait_time)
                    else:
                        raise exc
            else:
                raise FileNotFoundError("Файл vertex_sa.json не найден")
        except Exception as ve:
            logger.error(f"Ошибка фоллбэка Vertex AI для лида {lead['company_name']}: {ve}")
            lead.update({
                "role_guess": "Не определено",
                "pain_hypothesis": "Нехватка автоматизации",
                "offer_angle": "Разработка ИИ-ассистентов под ключ",
                "personal_hook": "Привет!",
                "generated_pitch": f"Привет! Увидел ваш профиль на {lead['source']}. Мы помогаем автоматизировать продажи с помощью ИИ. Интересно посмотреть примеры?",
                "offer_details": ["Разработка чат-ботов", "Настройка n8n"],
                "ai_score": 5
            })

    # Нормализация ai_score к типу int для сортировки и отчетов
    score = lead.get("ai_score", 5)
    try:
        if isinstance(score, str):
            if "/" in score:
                score = score.split("/")[0]
            lead["ai_score"] = int(score.strip())
        else:
            lead["ai_score"] = int(score)
    except Exception:
        lead["ai_score"] = 5


def save_local_results(leads, date_str):
    """Сохраняет результаты в CSV, Markdown-отчет и отдельные файлы"""
    base_dir = f"03_Marketing_and_Sales/daily_leads/{date_str}"
    os.makedirs(f"{base_dir}/details", exist_ok=True)
    
    # 1. Сохранение CSV
    csv_file = f"{base_dir}/leads_summary.csv"
    keys = ["company_name", "name", "phone", "email", "source", "query", "city", "url", "ai_score", "role_guess", "pain_hypothesis", "offer_angle", "personal_hook", "generated_pitch"]
    try:
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(leads)
        logger.info(f"CSV сохранен: {csv_file}")
    except Exception as e:
        logger.error(f"Ошибка сохранения CSV: {e}")

    # 2. Сохранение индивидуальных md файлов
    for idx, lead in enumerate(leads, 1):
        clean_company = re.sub(r'[^a-zA-Z0-9_а-яА-Я]', '_', lead['company_name'])
        detail_file = f"{base_dir}/details/{idx}_{clean_company}.md"
        
        details_content = f"""# Анализ Лида: {lead['company_name']}

- **ФИО контакта**: {lead.get('name', 'Не указано')}
- **Телефон**: {lead.get('phone') or 'Не указан'}
- **Email**: {lead.get('email') or 'Не указан'}
- **Источник**: {lead['source']}
- **Ключевой запрос**: {lead['query']}
- **Город**: {lead.get('city') or 'Не указан'}
- **Ссылка**: [{lead['source']}]({lead['url']})
- **Оценка ИИ (Relevance)**: {lead.get('ai_score', 5)}/10
- **Предполагаемая роль**: {lead.get('role_guess', 'Не указана')}

### 🔍 Анализ бизнеса и боли
- **Гипотеза о боли**: {lead.get('pain_hypothesis', '')}
- **Угол захода (Angle)**: {lead.get('offer_angle', '')}

### 💡 Что предложить этой компании:
"""
        offer_details = lead.get('offer_details', [])
        if isinstance(offer_details, list):
            for item in offer_details:
                details_content += f"- {item}\n"
        else:
            details_content += f"- {offer_details}\n"

        details_content += f"""
### ✉️ Драфт первого сообщения (WhatsApp / Telegram)
> {lead.get('generated_pitch', '')}
"""
        try:
            with open(detail_file, "w", encoding="utf-8") as f:
                f.write(details_content)
        except Exception as e:
            logger.error(f"Ошибка записи карточки лида {detail_file}: {e}")

    # 3. Сохранение главного Markdown отчета
    report_file = f"{base_dir}/leads_report.md"
    
    stats = {}
    for l in leads:
        stats[l['source']] = stats.get(l['source'], 0) + 1
        
    report_content = f"""# Отчет по лидогенерации от {date_str}

## 📊 Общая статистика сбора
- **Всего собрано лидов**: {len(leads)}
- Распределение по источникам:
"""
    for src, cnt in stats.items():
        report_content += f"  - **{src}**: {cnt} лидов\n"

    report_content += """
## 📋 Список лидов на сегодня

| № | Компания | Контакт | Источник | Оценка ИИ | Телефон | Ссылка |
|---|----------|---------|----------|-----------|---------|--------|
"""
    for idx, lead in enumerate(leads, 1):
        report_content += f"| {idx} | {lead['company_name']} | {lead.get('name', 'Не указано')} | `{lead['source']}` | **{lead.get('ai_score', 5)}** | {lead.get('phone') or '🚫'} | [Перейти]({lead['url']}) |\n"

    report_content += """
---
*Все индивидуальные драфты сообщений и коммерческие предложения сохранены в папке [details](./details).*
"""
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Markdown отчет сохранен: {report_file}")
    except Exception as e:
        logger.error(f"Ошибка сохранения отчета: {e}")

def write_leads_to_supabase(leads):
    """Записывает собранных лидов в Supabase, если настроены ключи"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase URL или KEY отсутствуют в .env. Запись в БД пропущена.")
        return
        
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        inserted_cnt = 0
        for lead in leads:
            phone = lead.get("phone")
            if not phone:
                continue
                
            norm_phone = normalize_phone_number(phone)
            if not norm_phone:
                continue
                
            # Проверим, нет ли уже такого лида
            res = supabase.table("leads").select("id").eq("phone", phone).execute()
            if res.data:
                logger.info(f"Лид с телефоном {phone} уже есть в базе. Пропускаем.")
                continue
                
            db_lead = {
                "phone": phone,
                "name": lead.get("name"),
                "company_name": lead.get("company_name"),
                "source": lead.get("source"),
                "niche": lead.get("query"),
                "city": lead.get("city"),
                "website": lead.get("url") if "http" in lead.get("url", "") else "",
                "role_guess": lead.get("role_guess"),
                "pain_hypothesis": lead.get("pain_hypothesis"),
                "offer_angle": lead.get("offer_angle"),
                "personal_hook": lead.get("personal_hook"),
                "generated_pitch": lead.get("generated_pitch"),
                "ai_score": int(lead.get("ai_score", 5)),
                "status": "new",
                "notes": f"Собрано автоматически {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
            supabase.table("leads").insert(db_lead).execute()
            inserted_cnt += 1
            
        logger.success(f"Записано новых лидов в Supabase: {inserted_cnt}")
    except Exception as e:
        logger.error(f"Ошибка записи в Supabase: {e}")

def send_telegram_notification(leads):
    """Отправляет структурированный отчет и контакты топ-лидов в Telegram"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logger.warning("Telegram Bot Token или Chat ID не настроены в .env. Отправка отчета в TG пропущена.")
        return
        
    logger.info("Отправка отчета в Telegram...")
    
    total_leads = len(leads)
    leads_with_contacts_list = [l for l in leads if l.get("phone") or l.get("email")]
    leads_with_contacts = len(leads_with_contacts_list)
    leads_with_contacts_list.sort(key=lambda x: int(x.get("ai_score", 0)), reverse=True)
    top_leads = leads_with_contacts_list[:5]
    
    # 1. Формируем главное сообщение со статистикой
    summary_message = (
        f"📊 *Отчет по лидогенерации от {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        f"✅ *Задача выполнена успешно!*\n"
        f"🔹 Всего собрано лидов: *{total_leads}*\n"
        f"📞 Лидов с контактами: *{leads_with_contacts}*\n"
        f"🔥 Горячих офферов сгенерировано: *{len(top_leads)}*\n\n"
        f"📂 Результаты сохранены на твоем Mac в папку:\n"
        f"`03_Marketing_and_Sales/daily_leads/{datetime.now().strftime('%Y-%m-%d')}/`"
    )
    
    # Отправляем сводку
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": TG_CHAT_ID,
            "text": summary_message,
            "parse_mode": "Markdown"
        }, timeout=10)
    except Exception as e:
        logger.error(f"Не удалось отправить сводку в Telegram: {e}")
        return

    # 2. Отправляем карточки ТОП-лидов по очереди
    if top_leads:
        try:
            requests.post(url, json={
                "chat_id": TG_CHAT_ID,
                "text": "🎯 *ТОП-5 горячих лидов с контактами на сегодня:*",
                "parse_mode": "Markdown"
            }, timeout=10)
            
            for idx, lead in enumerate(top_leads, 1):
                contact_info = []
                if lead.get("phone"):
                    contact_info.append(f"📞 *Тел:* `{lead['phone']}`")
                if lead.get("email"):
                    contact_info.append(f"✉️ *Email:* `{lead['email']}`")
                
                contacts_str = "\n".join(contact_info) if contact_info else "🚫 Контакты не найдены"
                
                lead_message = (
                    f"🔥 *Лид №{idx} | Оценка ИИ: {lead.get('ai_score', 5)}/10*\n\n"
                    f"🏢 *Компания:* {lead['company_name']}\n"
                    f"📍 *Город:* {lead.get('city', 'Не указан')}\n"
                    f"💼 *Контекст боли:* {lead.get('pain_hypothesis', 'Нехватка автоматизации')}\n"
                    f"🔗 [Ссылка на источник]({lead['url']})\n\n"
                    f"📇 *КОНТАКТЫ ДЛЯ СВЯЗИ:*\n{contacts_str}\n\n"
                    f"💬 *ДРАФТ СООБЩЕНИЯ (скопируй и отправь):*\n"
                    f"_{lead.get('generated_pitch', '')}_"
                )
                
                requests.post(url, json={
                    "chat_id": TG_CHAT_ID,
                    "text": lead_message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }, timeout=10)
                time.sleep(1) # Защита от спам-фильтра Telegram API
                
        except Exception as e:
            logger.error(f"Ошибка отправки карточек лидов в Telegram: {e}")

def load_enrichment_cache(date_str):
    cache_path = f"03_Marketing_and_Sales/daily_leads/{date_str}/enrichment_cache.json"
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша обогащения: {e}")
    return {}

def save_enrichment_cache(cache, date_str):
    base_dir = f"03_Marketing_and_Sales/daily_leads/{date_str}"
    os.makedirs(base_dir, exist_ok=True)
    cache_path = f"{base_dir}/enrichment_cache.json"
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения кэша обогащения: {e}")

def main():
    global use_vertex_directly

    logger.info("=== Запуск ежедневной лидогенерации ===")
    
    # Выбор ключа и инициализация клиента с учетом AIHubMix
    aihubmix_key = os.getenv("AIHUBMIX_API_KEY")
    if aihubmix_key:
        logger.info("Используем AIHubMix в качестве провайдера OpenAI API.")
        openai_client = OpenAI(
            api_key=aihubmix_key.strip().rstrip('.'),
            base_url="https://api.aihubmix.com/v1"
        )
    elif OPENAI_API_KEY:
        clean_key = OPENAI_API_KEY.strip().rstrip('.')
        if clean_key.startswith("sk-8EobY"):
            logger.info("Обнаружен ключ AIHubMix в OPENAI_API_KEY. Используем base_url AIHubMix.")
            openai_client = OpenAI(
                api_key=clean_key,
                base_url="https://api.aihubmix.com/v1"
            )
        else:
            openai_client = OpenAI(api_key=clean_key)
    else:
        logger.warning("Ключи API (OPENAI_API_KEY / AIHUBMIX_API_KEY) отсутствуют в .env. Будет использоваться только Vertex AI.")
        openai_client = None
        use_vertex_directly = True

    # Быстрая проверка работоспособности OpenAI/AIHubMix API ключа
    if openai_client and not use_vertex_directly:
        logger.info("Проверка работоспособности OpenAI/AIHubMix API ключа...")
        try:
            # Делаем сверхбыстрый запрос для проверки
            openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=3,
                timeout=5
            )
            logger.info("OpenAI/AIHubMix API ключ успешно проверен и работает.")
        except Exception as te:
            logger.warning(f"Ошибка проверки OpenAI/AIHubMix API ключа: {te}. Автоматически переключаемся на Vertex AI для всех лидов.")
            use_vertex_directly = True
            openai_client = None
    
    # 1. Сбор с HeadHunter
    hh_leads = collect_hh_leads()
    logger.info(f"Собрано лидов с HH.ru/HH.kz: {len(hh_leads)}")
    
    # 2. Сбор внешних лидов (Adata.kz / Threads.net)
    external_leads = load_external_leads()
    logger.info(f"Загружено внешних лидов (Adata / Threads): {len(external_leads)}")
    
    # 2.5 Загрузка судебных лидов (office.sud.kz)
    court_leads = load_court_leads()
    logger.info(f"Загружено судебных лидов: {len(court_leads)}")
    
    # Объединение и дедупликация
    all_leads = []
    seen_keys = set()
    
    for l in hh_leads + external_leads + court_leads:
        url = l.get("url", "")
        key = (l.get("company_name", "").strip().lower(), l.get("case_number", url).strip().lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        all_leads.append(l)
        
    logger.info(f"Всего лидов после объединения: {len(all_leads)}")
    
    # Поддержка ограничения количества лидов для тестирования
    limit = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=")[1])
                logger.info(f"Применен лимит на количество лидов: {limit}")
            except ValueError:
                pass
    if limit is not None:
        all_leads = all_leads[:limit]
        logger.info(f"Отрезано до {len(all_leads)} лидов.")
    
    # 3. ИИ Обогащение с кэшированием результатов
    date_str = datetime.now().strftime("%Y-%m-%d")
    cache = load_enrichment_cache(date_str)
    logger.info(f"Загружено {len(cache)} лидов из кэша обогащения.")
    
    for idx, l in enumerate(all_leads):
        url = l.get("url", "")
        has_contacts = bool(l.get("phone") or l.get("email"))
        
        # Проверяем, есть ли лид в кэше и имеет ли он сгенерированный питч
        if url and url in cache and cache[url].get("generated_pitch"):
            l.update(cache[url])
            logger.info(f"[{idx+1}/{len(all_leads)}] Лид {l['company_name']} восстановлен из кэша.")
        else:
            enrich_lead_with_ai(l, openai_client)
            if url:
                cache[url] = {
                    "role_guess": l.get("role_guess"),
                    "pain_hypothesis": l.get("pain_hypothesis"),
                    "offer_angle": l.get("offer_angle"),
                    "personal_hook": l.get("personal_hook"),
                    "generated_pitch": l.get("generated_pitch"),
                    "offer_details": l.get("offer_details"),
                    "ai_score": l.get("ai_score")
                }
                save_enrichment_cache(cache, date_str)
            time.sleep(0.2)
        
    # Нормализация ai_score для всех лидов (включая восстановленные из кэша)
    for l in all_leads:
        score = l.get("ai_score", 5)
        try:
            if isinstance(score, str):
                if "/" in score:
                    score = score.split("/")[0]
                l["ai_score"] = int(score.strip())
            else:
                l["ai_score"] = int(score)
        except Exception:
            l["ai_score"] = 5

    # Сортировка по оценке ИИ (более релевантные сверху)
    all_leads.sort(key=lambda x: x.get("ai_score", 5), reverse=True)
    
    # 4. Локальное сохранение результатов
    save_local_results(all_leads, date_str)
    
    # 5. Сохранение в БД Supabase (если доступно)
    write_leads_to_supabase(all_leads)
    
    # 6. Отправка отчета в Telegram
    send_telegram_notification(all_leads)
    
    logger.success(f"Ежедневная лидогенерация завершена успешно! Лидов обработано: {len(all_leads)}")

if __name__ == "__main__":
    main()
