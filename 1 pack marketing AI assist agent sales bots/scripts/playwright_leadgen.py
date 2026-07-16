import os
import sys
import re
import json
import time
import signal
from datetime import datetime
from loguru import logger
from playwright.sync_api import sync_playwright

# Игнорируем сигнал SIGHUP для предотвращения прерывания процесса при закрытии терминала в macOS
try:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except AttributeError:
    pass

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/playwright_leadgen.log", rotation="10 MB", retention="7 days", level="INFO")

CACHE_FILE = "06_Scripts_and_Tools/company_contacts_cache.json"
company_cache = {}

def load_company_cache():
    global company_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                company_cache = json.load(f)
            logger.info(f"Загружен кэш контактов компаний: {len(company_cache)} записей.")
        except Exception as e:
            logger.warning(f"Не удалось загрузить кэш компаний: {e}")
    else:
        logger.info("Кэш контактов компаний не найден, создаем новый.")

def save_company_cache():
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(company_cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Не удалось сохранить кэш контактов компаний: {e}")


def safe_goto(page, url, wait_until="domcontentloaded", timeout=20000, max_retries=3):
    """Выполняет безопасный переход на страницу с повторными попытками при таймаутах"""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Переход на {url} (попытка {attempt}/{max_retries})...")
            page.set_default_navigation_timeout(timeout)
            page.goto(url, wait_until=wait_until, timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Ошибка при переходе на {url} (попытка {attempt}): {e}")
            if attempt == max_retries:
                raise e
            time.sleep(attempt * 2)
    return False


def search_hh_web(page, query, area_id):
    """Ищет вакансии на hh.ru/hh.kz через браузер Playwright без использования API"""
    domain = "hh.ru" if area_id != 40 else "hh.kz"
    search_url = f"https://{domain}/search/vacancy?text={query}&area={area_id}&order_by=publication_time"
    
    logger.info(f"Открываем поиск HH: {search_url}")
    leads = []
    
    try:
        safe_goto(page, search_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        
        # Проверяем наличие вакансий на странице
        vacancy_cards = page.query_selector_all('[data-qa="vacancy-serp__vacancy"]')
        if not vacancy_cards:
            # Альтернативный селектор, если верстка обновилась
            vacancy_cards = page.query_selector_all('.serp-item')
            
        logger.info(f"Найдено карточек вакансий для '{query}' ({domain}): {len(vacancy_cards)}")
        
        for card in vacancy_cards[:5]:  # Берем топ-5 свежих вакансий для каждого запроса
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
                
                # Добавляем базовую информацию о лиде
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

def perform_uchet_search(page, query):
    """Выполняет поиск на pk.uchet.kz и возвращает страницу результатов"""
    logger.info(f"Выполняем ввод запроса '{query}' на pk.uchet.kz...")
    safe_goto(page, "https://pk.uchet.kz/search/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    # Находим поле ввода
    input_selector = 'input'
    page.wait_for_selector(input_selector, timeout=10000)
    page.click(input_selector)
    page.fill(input_selector, query)
    time.sleep(1)
    
    # Нажимаем Enter для поиска
    page.press(input_selector, 'Enter')
    time.sleep(5)

def get_uchet_company_info(page, company_name):
    # Ищет компанию на pk.uchet.kz и извлекает контакты (телефон, email, БИН, ЛПР)
    if company_name == "Не указано" or not company_name:
        return None
    
    # Очищаем название компании от лишних символов для поиска
    clean_name = re.sub(r'["\'«»]|ТОО|ИП|АО|товарищество с ограниченной ответственностью', '', company_name, flags=re.IGNORECASE).strip()
    cache_key = clean_name.lower()
    
    # Проверка кэша по имени компании
    if cache_key in company_cache:
        cached = company_cache[cache_key]
        if cached:
            logger.info(f"Компания '{company_name}' найдена в кэше по имени: {cached}")
            return cached
        else:
            logger.info(f"В кэше отмечено, что для '{company_name}' нет контактов. Пропускаем.")
            return None
            
    logger.info(f"Ищем контакты для {company_name} (запрос: {clean_name}) на pk.uchet.kz")
    
    try:
        perform_uchet_search(page, clean_name)
        
        # Извлекаем БИНы со страницы поиска
        text_content = page.content()
        bins = re.findall(r'(?:БИН|ИИН):\s*(\d{12})', text_content)
        bins = list(dict.fromkeys(bins))
        
        bin_num = bins[0] if bins else None
        
        if bin_num:
            # Проверка кэша по БИН
            if bin_num in company_cache:
                cached = company_cache[bin_num]
                if cached:
                    logger.info(f"Компания '{company_name}' (БИН {bin_num}) найдена в кэше по БИН.")
                    company_cache[cache_key] = cached
                    save_company_cache()
                    return cached
            
            company_url = f"https://pk.uchet.kz/search/bin/{bin_num}"
            logger.info(f"Переходим на страницу компании: {company_url}")
            safe_goto(page, company_url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            
            body_text = page.inner_text("body")
            
            # Поиск email и телефонов
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', body_text)
            valid_emails = [e for e in emails if not ("uchet" in e.lower() or e.endswith("uchet.kz"))]
            email = valid_emails[0] if valid_emails else ""
            
            phones = re.findall(r'(?:\+7|8)[\s\-]?\(?[7][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}', body_text)
            phone = phones[0] if phones else ""
            
            # Извлекаем ЛПР по селектору
            lpr_locator = page.locator("span:has-text('Руководитель:') + span").first
            lpr = lpr_locator.inner_text().strip() if lpr_locator.count() > 0 else ""
            
            # Если по селектору не нашли, пробуем мета-тег
            if not lpr:
                try:
                    meta_desc = page.locator("meta[name='description']").get_attribute("content")
                    lpr_match = re.search(r'Руководитель:\s*([^.]+)', meta_desc)
                    if lpr_match:
                        lpr = lpr_match.group(1).strip()
                except:
                    pass
            
            if not lpr:
                lpr = "Представитель компании"
                
            logger.info(f"Найденные контакты на pk.uchet.kz для {company_name}: ЛПР: {lpr}, Тел: {phone}, Email: {email}")
            result = {
                "name": lpr,
                "phone": phone,
                "email": email,
                "adata_url": company_url
            }
            
            # Сохраняем в кэш под обоими ключами
            company_cache[cache_key] = result
            company_cache[bin_num] = result
            save_company_cache()
            
            return result
        else:
            # Записываем в кэш пустой результат, чтобы не искать повторно
            company_cache[cache_key] = None
            save_company_cache()
            
    except Exception as e:
        logger.error(f"Ошибка при парсинге pk.uchet.kz для {company_name}: {e}")
        
    return None


def search_uchet_web(page, query):
    # Ищет компании на pk.uchet.kz по запросу и собирает контакты
    logger.info(f"Uchet: Поиск компаний по запросу '{query}'...")
    leads = []
    
    try:
        perform_uchet_search(page, query)
        
        # Извлекаем БИНы со страницы поиска
        text_content = page.content()
        bins = re.findall(r'(?:БИН|ИИН):\s*(\d{12})', text_content)
        bins = list(dict.fromkeys(bins))
                        
        logger.info(f"Найдено уникальных компаний на pk.uchet.kz по запросу '{query}': {len(bins)}")
        
        # Переходим в топ-3 компании для сбора контактов
        for bin_num in bins[:3]:
            try:
                comp_url = f"https://pk.uchet.kz/search/bin/{bin_num}"
                
                # Проверяем кэш по БИН
                if bin_num in company_cache:
                    cached = company_cache[bin_num]
                    if cached:
                        logger.info(f"Компания с БИН {bin_num} найдена в кэше. Пропускаем переход.")
                        leads.append({
                            "name": cached.get("name", "Представитель компании"),
                            "company_name": cached.get("company_name", "Неизвестно"),
                            "phone": cached.get("phone", ""),
                            "email": cached.get("email", ""),
                            "url": comp_url,
                            "description": f"Компания найдена на pk.uchet.kz по запросу: {query}. БИН: {bin_num}",
                            "source": "uchet.kz",
                            "city": cached.get("city", "Казахстан"),
                            "query": query
                        })
                        continue
                
                logger.info(f"Переходим на страницу компании {bin_num}: {comp_url}")
                safe_goto(page, comp_url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(3)
                
                body_text = page.inner_text("body")
                
                # Поиск email и телефонов
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', body_text)
                valid_emails = [e for e in emails if not ("uchet" in e.lower() or e.endswith("uchet.kz"))]
                email = valid_emails[0] if valid_emails else ""
                
                phones = re.findall(r'(?:\+7|8)[\s\-]?\(?[7][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}', body_text)
                phone = phones[0] if phones else ""
                
                # Название компании из h1 или h2
                company_name = "Неизвестно"
                h2_elem = page.locator("h2").first
                if h2_elem.count() > 0:
                    company_name = h2_elem.inner_text().strip()
                else:
                    h1_elem = page.locator("h1").first
                    if h1_elem.count() > 0:
                        company_name = h1_elem.inner_text().strip()
                
                # Извлекаем ЛПР по селектору
                lpr_locator = page.locator("span:has-text('Руководитель:') + span").first
                lpr_name = lpr_locator.inner_text().strip() if lpr_locator.count() > 0 else ""
                
                if not lpr_name:
                    try:
                        meta_desc = page.locator("meta[name='description']").get_attribute("content")
                        lpr_match = re.search(r'Руководитель:\s*([^.]+)', meta_desc)
                        if lpr_match:
                            lpr_name = lpr_match.group(1).strip()
                    except:
                        pass
                
                if not lpr_name:
                    lpr_name = "Представитель компании"
                    
                # Ищем город в адресе
                city = "Казахстан"
                addr_locator = page.locator("span:has-text('Юридический адрес:') + span").first
                if addr_locator.count() > 0:
                    addr_text = addr_locator.inner_text()
                    city_match = re.search(r'город\s+([А-Яа-яЁё]+)', addr_text, re.IGNORECASE) or \
                                 re.search(r'г\.\s*([А-Яа-яЁё]+)', addr_text, re.IGNORECASE)
                    if city_match:
                        city = city_match.group(1).strip()
                
                result = {
                    "name": lpr_name,
                    "company_name": company_name,
                    "phone": phone,
                    "email": email,
                    "url": comp_url,
                    "description": f"Компания найдена на pk.uchet.kz по запросу: {query}. БИН: {bin_num}",
                    "source": "uchet.kz",
                    "city": city,
                    "query": query
                }
                
                leads.append(result)
                
                # Сохраняем в кэш
                company_cache[bin_num] = result
                # Также сохраняем по названию компании
                clean_comp_name = re.sub(r'["\'«»]|ТОО|ИП|АО|товарищество с ограниченной ответственностью', '', company_name, flags=re.IGNORECASE).strip().lower()
                company_cache[clean_comp_name] = result
                save_company_cache()
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Ошибка при парсинге страницы компании {bin_num}: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка при работе с pk.uchet.kz по запросу {query}: {e}")
        
    return leads


def search_threads_web(page, query):
    """Ищет профили на threads.net по ключевому слову через Yahoo Search"""
    search_url = f"https://search.yahoo.com/search?q=site:threads.net+{query}"
    logger.info(f"Открываем поиск Threads в Yahoo Search: {search_url}")
    leads = []
    
    try:
        safe_goto(page, search_url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        
        html = page.content()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Находим все блоки результатов поиска Yahoo
        results = soup.select('ol.reg li') or soup.select('div.algo-sr')
        logger.info(f"Yahoo Search: Найдено блоков результатов для Threads по запросу '{query}': {len(results)}")
        
        from urllib.parse import unquote
        def clean_yahoo_url(url):
            if "r.search.yahoo.com" in url:
                match = re.search(r'/RU=([^/]+)', url)
                if match:
                    return unquote(match.group(1))
            return url
            
        for item in results:
            try:
                title_link = item.find('a')
                if not title_link:
                    continue
                href = title_link.get('href', '')
                cleaned_url = clean_yahoo_url(href)
                
                # Игнорируем служебные ссылки Yahoo
                if 'threads.net' not in cleaned_url or 'yahoo.com' in cleaned_url:
                    continue
                
                title = title_link.get_text().strip()
                
                snippet_div = item.find('div', class_='compText') or item.find('span', class_='fc-falcon') or item.find('div', class_='desc')
                snippet = snippet_div.get_text().strip() if snippet_div else ""
                
                # Пытаемся извлечь имя пользователя из URL или текста
                username = None
                match_url = re.search(r'threads\.net/@([a-zA-Z0-9_\.]+)', cleaned_url)
                if match_url:
                    username = match_url.group(1)
                else:
                    # Извлекаем из заголовка или сниппета (@username)
                    match_text = re.search(r'@([a-zA-Z0-9_\.]+)', title + " " + snippet)
                    if match_text:
                        username = match_text.group(1)
                
                if not username:
                    # Если не нашли юзернейм, сгенерируем временный из ID поста
                    match_post = re.search(r'/t/([a-zA-Z0-9_\-]+)', cleaned_url)
                    if match_post:
                        username = f"post_{match_post.group(1)}"
                    else:
                        username = "unknown"
                
                profile_url = f"https://www.threads.net/@{username}" if not username.startswith("post_") else cleaned_url
                
                # Извлекаем контакты из сниппета
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', snippet)
                phone_match = re.search(r'(?:\+7|8)[\s\-]?\(?[79][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}', snippet)
                
                email = email_match.group(0) if email_match else ""
                phone = phone_match.group(0) if phone_match else ""
                
                # Формируем имя для отображения
                display_name = title.replace(" - Threads", "").replace(" on Threads", "").strip()
                
                leads.append({
                    "name": display_name,
                    "company_name": f"Threads: @{username}" if not username.startswith("post_") else "Threads Post",
                    "phone": phone,
                    "email": email,
                    "url": profile_url,
                    "description": f"Профиль в Threads. Био/Пост: {snippet}",
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
    logger.info("=== Запуск устойчивого Playwright-парсера ===")
    load_company_cache()
    
    queries = ["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]
    # 40 - Казахстан (hh.kz), 1 - Москва (hh.ru)
    regions = [40, 1]
    
    # Парсинг аргументов командной строки
    quick_mode = "--quick" in sys.argv
    headless_mode = True
    
    for arg in sys.argv:
        if arg.startswith("--headless="):
            val = arg.split("=")[1].lower()
            headless_mode = (val == "true")
            
    if quick_mode:
        logger.info("Запуск в быстром режиме (--quick). Ограничиваем запросы.")
        queries = ["ии"]
        regions = [40]
        
    all_hh_leads = []
    all_threads_leads = []
    all_uchet_leads = []
    
    try:
        with sync_playwright() as p:
            # Запускаем браузер с эмуляцией реального пользователя и стабильными флагами для headless
            browser = p.chromium.launch(
                headless=headless_mode,
                args=[
                    "--disable-disable-blink-features",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            # Обходим детекты автоматизации и автоматически отклоняем все диалоги
            page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) }")
            page.on("dialog", lambda dialog: dialog.dismiss())

            
            # 1. Собираем вакансии с HH
            for area in regions:
                for query in queries:
                    leads = search_hh_web(page, query, area)
                    all_hh_leads.extend(leads)
                    time.sleep(3)  # Пауза между запросами для безопасности
            
            logger.info(f"Всего собрано кандидатов на лиды с HH: {len(all_hh_leads)}")
            
            # 2. Собираем профили с Threads.net
            for query in queries:
                leads = search_threads_web(page, query)
                all_threads_leads.extend(leads)
                time.sleep(3)
                
            logger.info(f"Всего собрано лидов с Threads.net: {len(all_threads_leads)}")
            
            # 3. Собираем компании напрямую с pk.uchet.kz по ключевым запросам
            for query in queries:
                leads = search_uchet_web(page, query)
                all_uchet_leads.extend(leads)
                time.sleep(3)
                
            logger.info(f"Всего собрано лидов напрямую с pk.uchet.kz: {len(all_uchet_leads)}")
            
            # 4. Обогащаем контактами из pk.uchet.kz для казахстанских компаний с HH
            enriched_leads = []
            for lead in all_hh_leads:
                if lead["source"] == "hh.kz":
                    contacts = get_uchet_company_info(page, lead["company_name"])
                    if contacts:
                        lead["phone"] = contacts["phone"]
                        lead["email"] = contacts["email"]
                        lead["url"] = contacts["adata_url"]
                        lead["name"] = contacts["name"]
                        lead["source"] = "uchet.kz"  # Меняем источник на uchet.kz, так как данные обогащены оттуда
                enriched_leads.append(lead)
                time.sleep(2)
                
            browser.close()
    except Exception as e:
        logger.error(f"Критическая ошибка при работе Playwright-парсера: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
        
    # Сохраняем результаты в файлы для последующего ИИ-обогащения в daily_leadgen.py
    output_path_external = "06_Scripts_and_Tools/external_leads.json"
    output_path_hh = "06_Scripts_and_Tools/hh_leads.json"
    
    try:
        # Внешние лиды включают uchet.kz (прямые + обогащенные) и threads.net
        external_data = [l for l in enriched_leads if l["source"] == "uchet.kz"] + all_uchet_leads + all_threads_leads
        hh_data = [l for l in enriched_leads if l["source"] != "uchet.kz"]
        
        with open(output_path_external, "w", encoding="utf-8") as f:
            json.dump(external_data, f, indent=4, ensure_ascii=False)
            
        with open(output_path_hh, "w", encoding="utf-8") as f:
            json.dump(hh_data, f, indent=4, ensure_ascii=False)
            
        logger.success("Данные успешно собраны и сохранены в локальных файлах для ИИ-обогащения!")
    except Exception as e:
        logger.error(f"Ошибка сохранения результатов: {e}")

if __name__ == "__main__":
    main()
