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

# Добавляем текущую директорию в sys.path для корректного импорта парсеров
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Импортируем существующие парсеры и функции записи в Supabase
from hh_parser import parse_hh
from adata_parser import search_adata
from threads_parser import parse_threads
from kaspijumys_parser import search_kaspi
from goszakup_parser import parse_goszakup
from contact_enricher import enrich_companies
from tax_analyzer import TaxAnalyzer
from main_parser import upsert_companies, upsert_vacancies, upsert_contacts

# Загружаем переменные окружения из корня проекта
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

# Инициализируем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Ниши / ключевые слова для ежедневного сбора
KEYWORDS = ["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]

# Путь для сохранения ежедневных результатов
OUTPUT_DIR_BASE = os.path.join(project_root, "03_Marketing_and_Sales", "daily_leads")

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY не найден в переменных окружения. ИИ-анализ будет пропущен.")
        return None
    clean_key = api_key.strip().rstrip('.')
    return OpenAI(api_key=clean_key)

def clean_company_name(name: str) -> str:
    """Очищает название компании от организационно-правовых форм для качественной дедупликации"""
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
    from google.oauth2 import service_account
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    
    sa_path = os.path.join(project_root, "vertex_sa.json")
    if not os.path.exists(sa_path):
        raise FileNotFoundError("Файл vertex_sa.json не найден")
        
    with open(sa_path, "r") as f:
        sa_info = json.load(f)
        project_id = sa_info.get("project_id")
        
    credentials = service_account.Credentials.from_service_account_file(sa_path)
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    
    def call_gemini():
        model = GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
        response = model.generate_content(
            user_prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return response.text.strip()
        
    loop = asyncio.get_event_loop()
    res_text = await loop.run_in_executor(None, call_gemini)
    return json.loads(res_text)

async def analyze_lead_with_ai(client, company: dict, vacancies: list) -> dict:
    """
    Анализирует компанию с помощью OpenAI: определяет боли, оффер и готовит текст сообщения.
    """
    comp_name = company.get("name", "Неизвестно")
    category = company.get("category", "")
    description = company.get("description", "")
    source = company.get("source", "")
    
    vac_titles = [v.get("title", "") for v in vacancies if v.get("company_id") == company.get("id")]
    vacancies_str = ", ".join(vac_titles) if vac_titles else "Нет активных вакансий в парсинге"
    
    prompt_system = (
        "разработки или маркетинга. Формула оффера: (Dream Outcome x Perceived Likelihood of Achievement) / (Time Delay x Effort & Sacrifice). "
        "Оффер должен быть настолько хорош, чтобы им было глупо отказываться.\n\n"
        "Отвечай строго в формате JSON, без использования markdown-разметки (без ```json ... ```).\n"
        "Формат JSON:\n"
        "{\n"
        '  "pain_points": ["конкретная боль", "потеря денег/времени", "страх"],\n'
        '  "outreach_angle": "убойный хук (1 предложение, почему мы пишем именно сейчас)",\n'
        '  "offer": "Гранд Слэм Оффер (гарантия результата, снятие рисков, скорость)",\n'
        '  "draft_pitch": "Сообщение для WhatsApp (3-5 коротких предложений. Заход через исследование/CustDev или жесткий оффер. Строго на русском, Имя ЛПР подставим позже, мощный CTA-вопрос в конце)"\n'
        "}"
    )
    
    prompt_user = (
        f"Проанализируй компанию:\n"
        f"Название: {comp_name}\n"
        f"Сфера деятельности: {category}\n"
        f"Описание: {description}\n"
        f"Источник: {source}\n"
        f"Открытые вакансии: {vacancies_str}\n\n"
        f"Сгенерируй боли, оффер и персонализированное первое сообщение (аутрич)."
    )

    if not client:
        log.warning(f"Клиент OpenAI отсутствует. Запуск Vertex AI фоллбэка для {comp_name}...")
        try:
            return await analyze_lead_with_vertex_ai(comp_name, category, description, source, vacancies_str, prompt_system, prompt_user)
        except Exception as ve:
            log.error(f"Ошибка Vertex AI для {comp_name}: {ve}")
            return {
                "pain_points": ["Не удалось провести ИИ-анализ: отсутствует API ключ"],
                "outreach_angle": "Связаться напрямую",
                "offer": "Предложить автоматизацию бизнес-процессов",
                "draft_pitch": "Здравствуйте! Увидели вашу компанию. Хотим предложить сотрудничество."
            }
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = re.sub(r"^```json\s*|```$", "", response_text, flags=re.MULTILINE)
            
        return json.loads(response_text)
    except Exception as e:
        log.error(f"Ошибка ИИ-анализа для компании {comp_name} через OpenAI: {e}. Пробуем фоллбэк на Vertex AI...")
        try:
            return await analyze_lead_with_vertex_ai(comp_name, category, description, source, vacancies_str, prompt_system, prompt_user)
        except Exception as ve:
            log.error(f"Ошибка фоллбэка Vertex AI для компании {comp_name}: {ve}")
            return {
                "pain_points": [f"Ошибка генерации: {str(e)}"],
                "outreach_angle": "Стандартный аутрич",
                "offer": f"Предложить услуги автоматизации в сфере {category}",
                "draft_pitch": f"Здравствуйте! Обратили внимание на компанию {comp_name}. Хотели бы предложить наши услуги автоматизации и маркетинга."
            }

async def collect_leads_for_keyword(keyword: str, max_pages: int = 2) -> dict:
    """Собирает лиды по одному ключевому слову со всех источников"""
    log.info(f"=== Запуск сбора по нише: '{keyword}' ===")
    
    hh_ru_task = parse_hh(city="россия", sphere=keyword, role="", max_pages=max_pages)
    hh_kz_task = parse_hh(city="казахстан", sphere=keyword, role="", max_pages=max_pages)
    adata_task = search_adata(city="Алматы", sphere=keyword, role="", max_pages=max_pages)
    kaspi_task = search_kaspi(city="Алматы", query=keyword, max_pages=max_pages)
    goszakup_task = parse_goszakup(keyword=keyword, max_pages=max_pages)
    threads_task = asyncio.to_thread(parse_threads, keyword)
    
    results = await asyncio.gather(hh_ru_task, hh_kz_task, adata_task, kaspi_task, goszakup_task, threads_task, return_exceptions=True)
    
    companies = []
    vacancies = []
    contacts = []
    
    sources = ["hh.ru", "hh.kz", "adata.kz", "kaspi.jobs", "goszakup", "threads.net"]
    for src, res in zip(sources, results):
        if isinstance(res, Exception):
            log.error(f"Ошибка парсера {src} для ниши '{keyword}': {res}")
            continue
        
        res_companies = res.get("companies", [])
        for c in res_companies:
            if src == "hh.ru" and c.get("source") == "hh.kz":
                c["source"] = "hh.ru"
            companies.append(c)
            
        vacancies.extend(res.get("vacancies", []))
        
        # Маркируем контакты из HH как HR, а из Госзакупок/Adata как ЛПР
        res_contacts = res.get("contacts", [])
        for contact in res_contacts:
            if src in ["hh.ru", "hh.kz", "kaspi.jobs"]:
                contact["role"] = "HR / Рекрутер (Вероятно не ЛПР)"
            elif src in ["goszakup", "adata.kz"]:
                contact["role"] = "ЛПР / Руководитель"
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
    
    log.info(f"Старт ежедневного сбора лидов за {date_str} (Тестовый режим: {test_mode})")
    log.info(f"Выходная папка: {output_dir}")
    
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
        await asyncio.sleep(2)
        
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
            
    log.info(f"Сбор завершен. Найдено компаний: {len(all_companies)} (уникальных: {len(unique_companies)})")
    
    if not unique_companies:
        log.warning("Собрано 0 уникальных лидов. Запись отменена.")
        return
        
    # --- Обогащение контактов ---
    log.info("Запуск обогащения контактов...")
    companies_to_enrich = unique_companies[:3] if test_mode else unique_companies
    enriched_companies = await enrich_companies(companies_to_enrich, max_concurrent=5)
    log.info(f"Обогащение завершено. Компаний с контактами: {sum(1 for c in enriched_companies if c.get('email') or c.get('phone'))}")
    
    # --- Налоговый анализ ---
    log.info("Запуск налогового анализа...")
    tax_analyzer = TaxAnalyzer()
    for c in enriched_companies:
        inn = c.get("inn") or c.get("bin")
        if inn:
            tax_data = tax_analyzer.analyze(inn)
            c["tax_analysis"] = tax_data
            c["tax_summary"] = tax_analyzer.format_for_report(tax_data)
        else:
            c["tax_analysis"] = {}
            c["tax_summary"] = "ℹ️ ИНН/БИН не указан — налоговый анализ невозможен"
    log.info("Налоговый анализ завершён.")
    
    # --- ИИ-анализ ---
    openai_client = get_openai_client()
    analyzed_companies = []
    
    log.info("Запуск ИИ-анализа...")
    companies_to_analyze = enriched_companies[:2] if test_mode else enriched_companies
    for idx, c in enumerate(companies_to_analyze):
        log.info(f"[{idx+1}/{len(companies_to_analyze)}] Анализ: {c.get('name')}")
        ai_analysis = await analyze_lead_with_ai(openai_client, c, all_vacancies)
        enriched_c = {**c, **ai_analysis}
        analyzed_companies.append(enriched_c)
        await asyncio.sleep(0.5)
        
    # --- Сохранение ---
    
    # JSON
    json_path = os.path.join(output_dir, "leads.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "leads": analyzed_companies,
            "vacancies": all_vacancies,
            "contacts": all_contacts
        }, f, ensure_ascii=False, indent=2)
        
    # CSV
    csv_path = os.path.join(output_dir, "leads.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Название компании", "Источник", "Ниша", "Город", "Сайт/Профиль", 
            "Телефон", "Email", "Telegram", "WhatsApp", "ИНН/БИН", "Оборот", "Сотрудники", 
            "Боли компании", "Угол захода", "Что предложить (Оффер)", "Драфт сообщения"
        ])
        for c in analyzed_companies:
            pains = ", ".join(c.get("pain_points", []))
            writer.writerow([
                c.get("name", ""),
                c.get("source", ""),
                c.get("category", ""),
                c.get("city", ""),
                c.get("site", "") or c.get("hh_url", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("telegram", ""),
                c.get("whatsapp", ""),
                c.get("inn") or c.get("bin", ""),
                TaxAnalyzer._fmt_money(c.get("tax_analysis", {}).get("data", {}).get("turnover", 0)),
                c.get("tax_analysis", {}).get("data", {}).get("employees", ""),
                pains,
                c.get("outreach_angle", ""),
                c.get("offer", ""),
                c.get("draft_pitch", "")
            ])
            
    # Markdown
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
        f.write(f"**Поисковые ниши:** {', '.join(KEYWORDS)}\n\n")
        
        f.write("## 📊 Статистика по источникам\n\n")
        f.write("| Источник | Количество лидов |\n")
        f.write("| :--- | :--- |\n")
        for src, leads in leads_by_source.items():
            f.write(f"| {src} | {len(leads)} |\n")
        f.write("\n---\n\n")
        
        f.write("## 📋 Сводная таблица\n\n")
        f.write("| Компания | Источник | Ниша | Город | Контакты | Угол захода |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for c in analyzed_companies:
            contacts_str = []
            if c.get("phone"):
                contacts_str.append(f"Тел: {c.get('phone')}")
            if c.get("email"):
                contacts_str.append(f"Email: {c.get('email')}")
            if c.get("telegram"):
                contacts_str.append(f"TG: {c.get('telegram')}")
            if c.get("whatsapp"):
                contacts_str.append(f"WA: {c.get('whatsapp')}")
            contact_final = "; ".join(contacts_str) if contacts_str else "Ссылка"
            
            link_url = c.get("site") or c.get("hh_url") or "#"
            comp_link = f"[{c.get('name')}]({link_url})"
            
            f.write(f"| {comp_link} | {c.get('source')} | {c.get('category')} | {c.get('city')} | {contact_final} | {c.get('outreach_angle')} |\n")
            
        f.write("\n---\n\n")
        f.write("## 🔍 Детализация и Персонализированные офферы\n\n")
        
        for idx, c in enumerate(analyzed_companies):
            f.write(f"### {idx+1}. 🏢 {c.get('name')} ({c.get('source')})\n\n")
            
            link_url = c.get("site") or c.get("hh_url") or ""
            if link_url:
                f.write(f"- **Ссылка/Сайт:** [{link_url}]({link_url})\n")
            f.write(f"- **Город:** {c.get('city')}\n")
            
            contacts_str = []
            if c.get("phone"):
                contacts_str.append(f"📞 {c.get('phone')}")
            if c.get("email"):
                contacts_str.append(f"📧 {c.get('email')}")
            if c.get("telegram"):
                contacts_str.append(f"✈️ {c.get('telegram')}")
            if c.get("whatsapp"):
                contacts_str.append(f"💬 {c.get('whatsapp')}")
            if contacts_str:
                f.write(f"- **Контакты:** {', '.join(contacts_str)}\n")
            
            f.write(f"- **Ниша:** {c.get('category')}\n")
            f.write(f"- **Описание:** {c.get('description')}\n")
            f.write(f"- **ИНН/БИН:** {c.get('inn') or c.get('bin', '—')}\n\n")
            
            # Налоговый блок
            tax_md = c.get("tax_summary", "")
            if tax_md and "❌" not in tax_md and "ℹ️" not in tax_md:
                f.write(tax_md + "\n\n")
            
            f.write("#### ⚠️ Предполагаемые боли:\n")
            for pain in c.get("pain_points", []):
                f.write(f"- {pain}\n")
            f.write("\n")
            
            f.write(f"#### 💡 Рекомендованный оффер:\n{c.get('offer')}\n\n")
            
    log.info(f"Сводные отчёты сохранены в {output_dir}")

    # --- Создание индивидуальных файлов лидов в папке details ---
    details_dir = os.path.join(output_dir, "details")
    os.makedirs(details_dir, exist_ok=True)
    log.info(f"Сохранение индивидуальных драфтов лидов в {details_dir}...")

    for idx, c in enumerate(analyzed_companies, start=1):
        raw_name = c.get("name") or f"lead_{idx}"
        safe_name = re.sub(r'[^\w\s-]', '', raw_name).strip().replace(" ", "_")
        if not safe_name:
            safe_name = f"lead_{idx}"
        detail_file = os.path.join(details_dir, f"{idx}_{safe_name}.md")
        
        with open(detail_file, "w", encoding="utf-8") as df:
            df.write(f"# Анализ Лида: {c.get('name')}\n\n")
            df.write(f"- **Телефон**: {c.get('phone') or 'Не указан'}\n")
            df.write(f"- **Email**: {c.get('email') or 'Не указан'}\n")
            df.write(f"- **Telegram**: {c.get('telegram') or 'Не указан'}\n")
            df.write(f"- **WhatsApp**: {c.get('whatsapp') or 'Не указан'}\n")
            df.write(f"- **Источник**: {c.get('source')}\n")
            df.write(f"- **Ключевой запрос**: {c.get('category')}\n")
            df.write(f"- **Город**: {c.get('city') or 'Казахстан/СНГ'}\n")
            link_target = c.get('site') or c.get('hh_url') or ''
            if link_target:
                df.write(f"- **Ссылка**: [{link_target}]({link_target})\n\n")
            else:
                df.write("- **Ссылка**: Нет ссылки\n\n")
                
            df.write("### 🔍 Анализ бизнеса и боли\n")
            for pain in c.get("pain_points", []):
                df.write(f"- {pain}\n")
            df.write(f"\n- **Угол захода (Angle)**: {c.get('outreach_angle')}\n\n")
            df.write("### 💡 Что предложить этой компании:\n")
            df.write(f"{c.get('offer')}\n\n")
            df.write("### ✉️ Драфт первого сообщения (WhatsApp / Telegram / Email)\n")
            df.write(f"> {c.get('draft_pitch')}\n")
    
    # --- Supabase ---
    supabase_configured = (
        os.getenv("SUPABASE_URL") and 
        os.getenv("SUPABASE_KEY") and 
        "YOUR_PROJECT" not in os.getenv("SUPABASE_URL")
    )
    
    if supabase_configured:
        log.info("Синхронизация с Supabase...")
        try:
            comp_count = await upsert_companies(analyzed_companies)
            vac_count = await upsert_vacancies(all_vacancies)
            
            supabase_contacts = []
            for c in analyzed_companies:
                if c.get("email") or c.get("phone"):
                    supabase_contacts.append({
                        "company_id": c.get("id"),
                        "vacancy_id": "",
                        "name": c.get("name"),
                        "role": "Компания / Профиль",
                        "email": c.get("email", ""),
                        "phone": c.get("phone", ""),
                        "contact_link": c.get("site") or c.get("hh_url", ""),
                        "source": c.get("source")
                    })
            supabase_contacts.extend(all_contacts)
            
            contact_count = await upsert_contacts(supabase_contacts)
            log.info(f"Supabase: +{comp_count} компаний, +{vac_count} вакансий, +{contact_count} контактов")
        except Exception as e:
            log.error(f"Ошибка Supabase: {e}")
    else:
        log.warning("Supabase не настроен. Пропускаем.")
        
    duration = datetime.now() - start_time
    log.info(f"Сбор завершён за {duration.total_seconds():.1f} сек.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Daily B2B Lead Aggregator")
    parser.add_argument("--test", action="store_true", help="Тестовый режим")
    args = parser.parse_args()
    
    asyncio.run(main(test_mode=args.test))