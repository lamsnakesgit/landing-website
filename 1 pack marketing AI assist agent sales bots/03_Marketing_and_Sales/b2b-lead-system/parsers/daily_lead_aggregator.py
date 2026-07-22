import os
import sys
import json
import csv
import re
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Добавляем текущую директорию в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from hh_parser import parse_hh
from adata_parser import search_adata_async
from threads_parser import parse_threads_async
from contact_enricher import enrich_companies
from tax_analyzer import TaxAnalyzer
from main_parser import upsert_companies, upsert_vacancies, upsert_contacts

project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Поисковые запросы по требованию пользователя
KEYWORDS = ["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]

OUTPUT_DIR_BASE = os.path.join(project_root, "03_Marketing_and_Sales", "daily_leads")

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY не найден. Будет использован Vertex AI.")
        return None
    clean_key = api_key.strip().rstrip('.')
    return OpenAI(api_key=clean_key)

def clean_company_name(name: str) -> str:
    if not name:
        return ""
    name_clean = name.lower()
    patterns = [
        r'\bтоо\b', r'\bип\b', r'\bооо\b', r'\bао\b', r'\bзао\b', r'\bпао\b',
        r'"', r"'", r'«', r'»', r'ltd', r'gmbh', r'limited'
    ]
    for pattern in patterns:
        name_clean = re.sub(pattern, '', name_clean)
    return name_clean.strip()

async def analyze_lead_with_vertex_ai(comp_name, category, description, source, vacancies_str, system_prompt, user_prompt) -> dict:
    """Осуществляет ИИ-анализ через Vertex AI HTTP REST API (Gemini 2.5 Flash)"""
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    import requests
    
    sa_path = os.path.join(project_root, "vertex_sa.json")
    if not os.path.exists(sa_path):
        raise FileNotFoundError("Файл vertex_sa.json не найден")
        
    with open(sa_path, "r", encoding="utf-8") as f:
        sa_info = json.load(f)
        project_id = sa_info.get("project_id")
        
    credentials = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    credentials.refresh(Request())
    
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    def call_http():
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        res_data = resp.json()
        text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```"):
            text = re.sub(r"^```json\s*|```$", "", text, flags=re.MULTILINE)
        return json.loads(text)
        
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, call_http)

async def analyze_lead_with_ai(client, company: dict, vacancies: list) -> dict:
    comp_name = company.get("name", "Неизвестно")
    category = company.get("category", "")
    description = company.get("description", "")
    source = company.get("source", "")
    director = company.get("director", "")
    
    vac_titles = [v.get("title", "") for v in vacancies if v.get("company_id") == company.get("id")]
    vacancies_str = ", ".join(vac_titles) if vac_titles else "Нет активных вакансий"
    
    prompt_system = (
        "Ты — высококлассный B2B эксперт по продажам ИИ-агентов, автоворонок, веб-разработки и перформанс-маркетинга.\n"
        "Твоя задача — проанализировать компанию/профиль лида и сформировать оффер и 1-е сообщение.\n"
        "Отвечай строго в формате JSON, без использования markdown-разметки (без ```json ... ```).\n"
        "Формат JSON:\n"
        "{\n"
        '  "pain_points": ["конкретная боль бизнеса", "потеря денег/клиентов/времени"],\n'
        '  "outreach_angle": "убойный хук (1 предложение, почему пишем именно им)",\n'
        '  "offer": "Конкретный оффер: что именно мы предлагаем этой компании (автоматизация, ИИ бот, CRM, контекст)",\n'
        '  "draft_pitch": "Первое сообщение для WhatsApp/Telegram (3-4 коротких предложения, персональное обращение, вопрос в конце)"\n'
        "}"
    )
    
    prompt_user = (
        f"Проанализируй лида:\n"
        f"Название/Профиль: {comp_name}\n"
        f"ЛПР/Руководитель: {director or 'Не указан'}\n"
        f"Ниша/Сфера: {category}\n"
        f"Описание: {description}\n"
        f"Источник: {source}\n"
        f"Вакансии: {vacancies_str}\n\n"
        f"Сгенерируй боли, оффер и драфт первого сообщения."
    )

    if not client:
        try:
            return await analyze_lead_with_vertex_ai(comp_name, category, description, source, vacancies_str, prompt_system, prompt_user)
        except Exception as ve:
            log.error(f"Ошибка Vertex AI для {comp_name}: {ve}")
            return {
                "pain_points": ["Высокие операционные расходы", "Рутинная обработка заявок вручную"],
                "outreach_angle": "Внедрение ИИ для ускорения продаж",
                "offer": "Разработка ИИ-агента квалификации и чат-бота для автоответов",
                "draft_pitch": f"Здравствуйте! Обратили внимание на {comp_name}. Мы помогаем внедрять ИИ-ботов для автоматизации работы с клиентами. Подскажите, актуально ли сейчас сократить время ответа клиентам?"
            }
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            temperature=0.7,
            max_tokens=800
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = re.sub(r"^```json\s*|```$", "", response_text, flags=re.MULTILINE)
            
        return json.loads(response_text)
    except Exception as e:
        log.error(f"Ошибка OpenAI для {comp_name}: {e}. Пробуем Vertex AI...")
        try:
            return await analyze_lead_with_vertex_ai(comp_name, category, description, source, vacancies_str, prompt_system, prompt_user)
        except Exception as ve:
            return {
                "pain_points": ["Необходимость масштабирования продаж"],
                "outreach_angle": "Оптимизация маркетинга и коммуникаций",
                "offer": f"Внедрение ИИ-решений и автоворонок для сферы {category}",
                "draft_pitch": f"Здравствуйте! Хотели предложить вам решения по автоматизации маркетинга и ИИ для {comp_name}. Подскажите, с кем можно обсудить детали?"
            }

async def collect_leads_for_keyword(keyword: str, max_pages: int = 2) -> dict:
    log.info(f"=== Запуск сбора по запросу: '{keyword}' ===")
    
    hh_ru_task = parse_hh(city="россия", sphere=keyword, role="", max_pages=max_pages)
    hh_kz_task = parse_hh(city="казахстан", sphere=keyword, role="", max_pages=max_pages)
    adata_task = search_adata_async(city="Алматы", sphere=keyword, role="", max_pages=1)
    threads_task = parse_threads_async(keyword, max_results=10)
    
    results = await asyncio.gather(hh_ru_task, hh_kz_task, adata_task, threads_task, return_exceptions=True)
    
    companies = []
    vacancies = []
    contacts = []
    
    sources = ["hh.ru", "hh.kz", "adata.kz", "threads.net"]
    for src, res in zip(sources, results):
        if isinstance(res, Exception):
            log.error(f"Ошибка парсера {src} для запроса '{keyword}': {res}")
            continue
        
        res_companies = res.get("companies", [])
        for c in res_companies:
            if src == "hh.ru" and c.get("source") == "hh.kz":
                c["source"] = "hh.ru"
            companies.append(c)
            
        vacancies.extend(res.get("vacancies", []))
        
        res_contacts = res.get("contacts", [])
        for contact in res_contacts:
            if src in ["hh.ru", "hh.kz"]:
                contact["role"] = "HR / Рекрутер"
            elif src == "adata.kz":
                contact["role"] = "Директор / Руководитель (ЛПР)"
        contacts.extend(res_contacts)
        
    return {
        "companies": companies,
        "vacancies": vacancies,
        "contacts": contacts
    }

async def main(test_mode: bool = False):
    start_time = datetime.now()
    date_str = start_time.strftime("%Y-%m-%d")
    output_dir = os.path.join(OUTPUT_DIR_BASE, date_str)
    os.makedirs(output_dir, exist_ok=True)
    
    log.info(f"🚀 Ежедневный сбор лидов за {date_str} (Тестовый режим: {test_mode})")
    log.info(f"Папка сохранения: {output_dir}")
    
    all_companies = []
    all_vacancies = []
    all_contacts = []
    
    keywords_to_run = ["боты"] if test_mode else KEYWORDS
    max_pages = 1 if test_mode else 2
    
    for kw in keywords_to_run:
        kw_data = await collect_leads_for_keyword(kw, max_pages=max_pages)
        all_companies.extend(kw_data["companies"])
        all_vacancies.extend(kw_data["vacancies"])
        all_contacts.extend(kw_data["contacts"])
        await asyncio.sleep(1)
        
    # --- Дедупликация ---
    seen_names = set()
    unique_companies = []
    
    for c in all_companies:
        name = c.get("name", "")
        clean_name = clean_company_name(name)
        if not clean_name:
            continue
        if clean_name not in seen_names:
            seen_names.add(clean_name)
            unique_companies.append(c)
            
    log.info(f"Сбор завершен. Все компаний: {len(all_companies)}, Уникальных: {len(unique_companies)}")
    
    if not unique_companies:
        log.warning("Собрано 0 уникальных лидов.")
        return
        
    # --- Обогащение ---
    log.info("Обогащение контактов...")
    companies_to_enrich = unique_companies[:3] if test_mode else unique_companies
    enriched_companies = await enrich_companies(companies_to_enrich, max_concurrent=5)
    
    # --- ИИ-анализ (Генерация офферов и драфтов сообщений) ---
    openai_client = get_openai_client()
    analyzed_companies = []
    
    log.info("Запуск ИИ-анализа и генерации 1-х сообщений + офферов...")
    companies_to_analyze = enriched_companies[:3] if test_mode else enriched_companies
    for idx, c in enumerate(companies_to_analyze):
        log.info(f"[{idx+1}/{len(companies_to_analyze)}] ИИ-анализ: {c.get('name')}")
        ai_analysis = await analyze_lead_with_ai(openai_client, c, all_vacancies)
        enriched_c = {**c, **ai_analysis}
        analyzed_companies.append(enriched_c)
        await asyncio.sleep(0.3)
        
    # --- Сохранение JSON ---
    json_path = os.path.join(output_dir, "leads.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "leads": analyzed_companies,
            "vacancies": all_vacancies,
            "contacts": all_contacts
        }, f, ensure_ascii=False, indent=2)
        
    # --- Сохранение CSV ---
    csv_path = os.path.join(output_dir, "leads.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Компания / Профиль", "Источник", "Ниша", "Город", "Ссылка", 
            "Телефон", "Email", "ИНН/БИН", "Боли компании", "Угол захода", "Что предложить (Оффер)", "Драфт 1-го сообщения"
        ])
        for c in analyzed_companies:
            pains = ", ".join(c.get("pain_points", []))
            writer.writerow([
                c.get("name", ""),
                c.get("source", ""),
                c.get("category", ""),
                c.get("city", ""),
                c.get("site") or c.get("hh_url", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("inn") or c.get("bin", ""),
                pains,
                c.get("outreach_angle", ""),
                c.get("offer", ""),
                c.get("draft_pitch", "")
            ])
            
    # --- Сохранение Markdown Сводки ---
    md_path = os.path.join(output_dir, "leads_summary.md")
    
    leads_by_source = {}
    for c in analyzed_companies:
        src = c.get("source", "Другие")
        if src not in leads_by_source:
            leads_by_source[src] = []
        leads_by_source[src].append(c)
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 Ежедневный Отчет по Лидогенерации — {date_str}\n\n")
        f.write(f"**Дата сбора:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write(f"**Всего уникальных лидов:** {len(analyzed_companies)}\n")
        f.write(f"**Поисковые запросы:** {', '.join(KEYWORDS)}\n\n")
        
        f.write("## 📊 Статистика по источникам\n\n")
        f.write("| Источник | Количество лидов |\n")
        f.write("| :--- | :--- |\n")
        for src, leads in leads_by_source.items():
            f.write(f"| {src} | {len(leads)} |\n")
        f.write("\n---\n\n")
        
        f.write("## 📋 Сводная таблица лидов\n\n")
        f.write("| Компания | Источник | Запрос | Контакты | Что предложить | Драфт сообщения |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for c in analyzed_companies:
            contacts_str = []
            if c.get("phone"):
                contacts_str.append(f"Тел: {c.get('phone')}")
            if c.get("email"):
                contacts_str.append(f"Email: {c.get('email')}")
            contact_final = "; ".join(contacts_str) if contacts_str else "Ссылка"
            
            link_url = c.get("site") or c.get("hh_url") or "#"
            comp_link = f"[{c.get('name')}]({link_url})"
            
            f.write(f"| {comp_link} | {c.get('source')} | {c.get('category')} | {contact_final} | {c.get('offer')} | {c.get('draft_pitch')} |\n")
            
        f.write("\n---\n\n")
        f.write("## 🔍 Детализация по каждому лиду\n\n")
        
        for idx, c in enumerate(analyzed_companies, start=1):
            f.write(f"### {idx}. 🏢 {c.get('name')} ({c.get('source')})\n\n")
            
            link_url = c.get("site") or c.get("hh_url") or ""
            if link_url:
                f.write(f"- **Ссылка/Сайт:** [{link_url}]({link_url})\n")
            f.write(f"- **Город:** {c.get('city')}\n")
            
            contacts_str = []
            if c.get("phone"):
                contacts_str.append(f"📞 {c.get('phone')}")
            if c.get("email"):
                contacts_str.append(f"📧 {c.get('email')}")
            if contacts_str:
                f.write(f"- **Контакты:** {', '.join(contacts_str)}\n")
            
            f.write(f"- **Запрос:** {c.get('category')}\n")
            f.write(f"- **Описание:** {c.get('description')}\n\n")
            
            f.write("#### ⚠️ Боли компании:\n")
            for pain in c.get("pain_points", []):
                f.write(f"- {pain}\n")
            f.write("\n")
            
            f.write(f"#### 💡 Что предложить этой компании (Оффер):\n{c.get('offer')}\n\n")
            f.write(f"#### ✉️ Драфт 1-го сообщения:\n> {c.get('draft_pitch')}\n\n")

    # --- Создание отдельного .md файла для КАЖДОГО лида в папке details/ ---
    details_dir = os.path.join(output_dir, "details")
    os.makedirs(details_dir, exist_ok=True)
    log.info(f"Сохранение персональных файлов с драфтами в {details_dir}...")

    for idx, c in enumerate(analyzed_companies, start=1):
        raw_name = c.get("name") or f"lead_{idx}"
        safe_name = re.sub(r'[^a-zA-Z0-9_]+', '_', raw_name).strip('_')
        if not safe_name:
            safe_name = f"lead_{idx}"
        detail_file = os.path.join(details_dir, f"{idx}_{safe_name}.md")
        
        with open(detail_file, "w", encoding="utf-8") as df:
            df.write(f"# Карточка Лида: {c.get('name')}\n\n")
            df.write(f"- **Источник**: {c.get('source')}\n")
            df.write(f"- **Запрос**: {c.get('category')}\n")
            df.write(f"- **Город**: {c.get('city') or 'Казахстан/СНГ'}\n")
            df.write(f"- **Телефон**: {c.get('phone') or 'Не указан'}\n")
            df.write(f"- **Email**: {c.get('email') or 'Не указан'}\n")
            link_target = c.get('site') or c.get('hh_url') or ''
            if link_target:
                df.write(f"- **Ссылка/Профиль**: [{link_target}]({link_target})\n\n")
            else:
                df.write("- **Ссылка/Профиль**: Нет ссылки\n\n")
                
            df.write("### ⚠️ Боли и анализ компании\n")
            for pain in c.get("pain_points", []):
                df.write(f"- {pain}\n")
            df.write(f"\n- **Угол захода (Angle)**: {c.get('outreach_angle')}\n\n")
            
            df.write("### 💡 Что предложить этой компании (Оффер):\n")
            df.write(f"{c.get('offer')}\n\n")
            
            df.write("### ✉️ Драфт 1-го сообщения для связи (WhatsApp / Telegram):\n")
            df.write(f"> {c.get('draft_pitch')}\n")

    duration = datetime.now() - start_time
    log.info(f"🎉 Ежедневный сбор успешно завершён за {duration.total_seconds():.1f} сек. Результаты сохранены в {output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Daily B2B Lead Aggregator")
    parser.add_argument("--test", action="store_true", help="Тестовый режим (только 1 запрос 'боты')")
    args = parser.parse_args()
    
    asyncio.run(main(test_mode=args.test))