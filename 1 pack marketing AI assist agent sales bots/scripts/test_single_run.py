import os
import re
import json
import time
from datetime import datetime
from loguru import logger
from playwright.sync_api import sync_playwright

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/test_single_run.log", rotation="10 MB", retention="7 days", level="INFO")

def search_hh_web(page, query, area_id):
    domain = "hh.ru" if area_id != 40 else "hh.kz"
    search_url = f"https://{domain}/search/vacancy?text={query}&area={area_id}&order_by=publication_time"
    logger.info(f"Открываем поиск HH: {search_url}")
    leads = []
    
    try:
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        vacancy_cards = page.query_selector_all('[data-qa="vacancy-serp__vacancy"]')
        if not vacancy_cards:
            vacancy_cards = page.query_selector_all('.serp-item')
            
        logger.info(f"Найдено карточек вакансий для '{query}' ({domain}): {len(vacancy_cards)}")
        
        for card in vacancy_cards[:2]:  # Возьмем топ-2
            try:
                title_elem = card.query_selector('[data-qa="serp-item__title"]') or card.query_selector('.serp-item__title')
                if not title_elem:
                    continue
                
                title = title_elem.inner_text().strip()
                url = title_elem.get_attribute("href")
                if url and not url.startswith("http"):
                    url = f"https://{domain}{url}"
                
                company_elem = card.query_selector('[data-qa="vacancy-serp__vacancy-employer"]') or card.query_selector('.vacancy-serp-item__meta-info-company')
                company_name = company_elem.inner_text().strip() if company_elem else "Не указано"
                
                city_elem = card.query_selector('[data-qa="vacancy-serp__vacancy-address"]') or card.query_selector('.vacancy-serp__vacancy-address')
                city = city_elem.inner_text().strip() if city_elem else ""
                
                leads.append({
                    "name": "Представитель компании",
                    "company_name": company_name,
                    "phone": "",
                    "email": "",
                    "url": url,
                    "description": f"Вакансия: {title}",
                    "source": domain,
                    "city": city,
                    "query": query
                })
            except Exception as e:
                logger.error(f"Ошибка при парсинге карточки вакансии HH: {e}")
    except Exception as e:
        logger.error(f"Ошибка при работе с HH: {e}")
        
    return leads

def get_adata_company_info(page, company_name):
    if company_name == "Не указано" or not company_name:
        return None
    
    clean_name = re.sub(r'["\'«»]|ТОО|ИП|АО', '', company_name).strip()
    search_url = f"https://adata.kz/search?q={clean_name}"
    logger.info(f"Ищем контакты для {company_name} на adata.kz: {search_url}")
    
    try:
        page.goto(search_url, wait_until="networkidle", timeout=20000)
        time.sleep(2)
        
        first_result = page.query_selector("a.search-result-link") or page.query_selector(".search-results a")
        if first_result:
            company_url = first_result.get_attribute("href")
            if company_url:
                if not company_url.startswith("http"):
                    company_url = f"https://adata.kz{company_url}"
                
                logger.info(f"Переходим на страницу компании: {company_url}")
                page.goto(company_url, wait_until="networkidle", timeout=20000)
                time.sleep(2)
                
                body_text = page.inner_text("body")
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', body_text)
                email = emails[0] if emails else ""
                
                phones = re.findall(r'(?:\+7|8)[\s\-]?\(?[7][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}', body_text)
                phone = phones[0] if phones else ""
                
                logger.info(f"Контакты на adata.kz: Тел: {phone}, Email: {email}")
                return {"phone": phone, "email": email, "adata_url": company_url}
    except Exception as e:
        logger.error(f"Ошибка при парсинге adata.kz для {company_name}: {e}")
        
    return None

def search_threads_web(page, query):
    search_url = f"https://html.duckduckgo.com/html/?q=site:threads.net+{query}"
    logger.info(f"Открываем поиск Threads в DuckDuckGo: {search_url}")
    leads = []
    
    try:
        page.goto(search_url, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        result_elements = page.query_selector_all('.result__body')
        logger.info(f"DDG HTML: Найдено блоков для Threads по запросу '{query}': {len(result_elements)}")
        
        for element in result_elements[:2]:  # Топ-2 для теста
            try:
                title_elem = element.query_selector('.result__title a')
                snippet_elem = element.query_selector('.result__snippet')
                
                if not title_elem:
                    continue
                    
                title = title_elem.inner_text().strip()
                url = title_elem.get_attribute("href")
                snippet = snippet_elem.inner_text().strip() if snippet_elem else ""
                
                match = re.search(r'threads\.net/@([a-zA-Z0-9_\.]+)', url)
                if match:
                    username = match.group(1)
                    profile_url = f"https://www.threads.net/@{username}"
                    
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', snippet)
                    phone_match = re.search(r'(?:\+7|8)[\s\-]?\(?[79][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}', snippet)
                    
                    email = email_match.group(0) if email_match else ""
                    phone = phone_match.group(0) if phone_match else ""
                    
                    display_name = title.replace(" - Threads", "").replace(" (@" + username + ")", "").strip()
                    if display_name == "Threads":
                        display_name = f"Профиль Threads @{username}"
                    
                    leads.append({
                        "name": display_name,
                        "company_name": f"Threads: @{username}",
                        "phone": phone,
                        "email": email,
                        "url": profile_url,
                        "description": f"Профиль в Threads. Био: {snippet}",
                        "source": "threads.net",
                        "city": "СНГ",
                        "query": query
                    })
            except Exception as e:
                logger.error(f"Ошибка при парсинге результата Threads: {e}")
    except Exception as e:
        logger.error(f"Ошибка при поиске Threads: {e}")
        
    return leads

def main():
    logger.info("=== Запуск ТЕСТОВОГО сбора ===")
    
    # Всего один запрос для быстроты теста
    queries = ["разработка ботов"]
    regions = [40, 1]  # Казахстан и Москва
    
    all_hh_leads = []
    all_threads_leads = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-disable-blink-features", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) }")
        
        # 1. Собираем вакансии с HH
        for area in regions:
            for query in queries:
                leads = search_hh_web(page, query, area)
                all_hh_leads.extend(leads)
                time.sleep(1)
        
        logger.info(f"Всего собрано кандидатов на лиды с HH: {len(all_hh_leads)}")
        
        # 2. Собираем профили с Threads.net
        for query in queries:
            leads = search_threads_web(page, query)
            all_threads_leads.extend(leads)
            time.sleep(1)
            
        logger.info(f"Всего собрано лидов с Threads.net: {len(all_threads_leads)}")
        
        # 3. Обогащаем контактами из Adata.kz для казахстанских компаний
        enriched_leads = []
        for lead in all_hh_leads:
            if lead["source"] == "hh.kz" and lead["company_name"] != "Не указано":
                contacts = get_adata_company_info(page, lead["company_name"])
                if contacts:
                    lead["phone"] = contacts["phone"]
                    lead["email"] = contacts["email"]
                    lead["url"] = contacts["adata_url"]
                    lead["source"] = "adata.kz"
            enriched_leads.append(lead)
            time.sleep(1)
            
        browser.close()
        
    # Сохраняем тестовые результаты
    output_path_external = "06_Scripts_and_Tools/test_external_leads.json"
    output_path_hh = "06_Scripts_and_Tools/test_hh_leads.json"
    
    external_data = [l for l in enriched_leads if l["source"] == "adata.kz"] + all_threads_leads
    hh_data = [l for l in enriched_leads if l["source"] != "adata.kz"]
    
    with open(output_path_external, "w", encoding="utf-8") as f:
        json.dump(external_data, f, indent=4, ensure_ascii=False)
        
    with open(output_path_hh, "w", encoding="utf-8") as f:
        json.dump(hh_data, f, indent=4, ensure_ascii=False)
        
    logger.success("Тестовый сбор завершен успешно!")

if __name__ == "__main__":
    main()
