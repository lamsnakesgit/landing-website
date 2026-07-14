import json
import csv
import time
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def normalize_city(court_name):
    """Определяет город по названию суда"""
    court_lower = court_name.lower()
    cities = [
        "алматы", "астана", "шымкент", "караганда", "актобе", "тараз", "павлодар", 
        "усть-каменогорск", "семей", "кокшетау", "костанай", "атырау", "актау", 
        "кызылорда", "уральск", "петропавловск", "туркестан", "талдыкорган", 
        "конаев", "жезказган"
    ]
    for city in cities:
        if city in court_lower:
            return city.capitalize()
    return "Казахстан"

def extract_entities(parties_str):
    """
    Разбирает строку сторон судебного дела.
    Возвращает словарь {"company": ..., "person": ...}
    """
    parts = [p.strip() for p in parties_str.split(',') if p.strip()]
    company = ""
    person = ""
    
    org_keywords = [
        "тоо", "ао", "ип", "гкп", "ргп", "ргу", "кгу", "гу", "пхв", "оо ", "кооператив", 
        "товарищество", "акционерное", "общество", "предприятие", "учреждение", 
        "департамент", "министерство", "управление", "войсковая часть", "банк", 
        "акимат", "комитет", "прокуратура", "школа", "больница", "колледж", "институт"
    ]
    
    for part in parts:
        part_lower = part.lower()
        is_org = False
        for kw in org_keywords:
            if kw in part_lower:
                is_org = True
                break
        
        if is_org:
            if not company:
                company = part
        else:
            if not person:
                # Ограничиваем длину ФИО, чтобы не взять случайный текст
                if len(part.split()) <= 4:
                    person = part
                    
    if not company and parts:
        for part in parts:
            if len(part) > 35:
                company = part
                break
                
    return {
        "company": company or "Не указано",
        "person": person or "Не указано"
    }

def parse_labor_cases(max_pages=5):
    print("🤖 Запуск фонового парсера судебных дел по Трудовому кодексу...")
    
    if not os.path.exists("sud_state.json"):
        print("❌ Ошибка: Файл sud_state.json не найден. Сначала запустите auth_stealth.py!")
        return False

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"03_Marketing_and_Sales/daily_leads/{date_str}"
    os.makedirs(output_dir, exist_ok=True)
    
    raw_cases = []
    court_leads = []

    with sync_playwright() as p:
        print("🌐 Попытка зайти в Банк судебных актов в фоновом режиме (headless=True)...")
        browser = p.chromium.launch(
            headless=True, 
            args=[
                "--disable-disable-blink-features",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--ignore-certificate-errors"
            ]
        )
        context = browser.new_context(
            storage_state="sud_state.json" if os.path.exists("sud_state.json") else None, 
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        # Автоматически закрываем все диалоговые окна
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        # Переход с жестким таймаутом в 20 секунд
        try:
            page.set_default_navigation_timeout(20000)
            page.goto("https://office.sud.kz/form/courtActs/index.xhtml", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ Ошибка перехода на судебный кабинет (таймаут или сайт недоступен): {e}")
            browser.close()
            return False
        
        # Проверяем, авторизованы ли мы
        content = page.content()
        is_logged_in = "Выход" in content or "Шығу" in content
        
        if not is_logged_in:
            print("❌ Ошибка: Сессия в sud_state.json недействительна или отсутствует.")
            print("Пожалуйста, перейдите на страницу https://office.sud.kz/ и выполните вход с помощью ЭЦП,")
            print("предварительно запустив скрипт авторизации: python scripts/sud_parser/auth_stealth.py")
            browser.close()
            return False
            
        print("✅ Авторизация успешна (сессия восстановлена).")
        
        # Закрываем модальное окно, если оно есть
        try:
            page.locator("text=Жабу").click(timeout=3000)
            page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # Выбираем русский язык
        try:
            page.evaluate("selectLanguageRu(window.location)")
            page.wait_for_timeout(3000)
        except Exception as e:
            print("⚠️ Не удалось переключить язык:", e)
            
        # Открываем Расширенный поиск
        print("🔍 Открываем расширенный поиск...")
        try:
            page.wait_for_selector("#filter-button", timeout=15000)
            page.locator("#filter-button").click()
            page.wait_for_timeout(2000)
        except Exception as e:
            print("❌ Ошибка открытия расширенного поиска:", e)
            page.screenshot(path="debug_search_error.png")
            with open("debug_search_error.html", "w") as f:
                f.write(page.content())
            browser.close()
            return False
            
        # Выбираем 2024 год
        print("📅 Выбираем год (2024)...")
        try:
            page.evaluate('''() => {
                var select = document.querySelector("select[name$='edit-period']");
                if (select && select.selectize) {
                    select.selectize.setValue("2024");
                } else if (select) {
                    select.value = "2024";
                    select.dispatchEvent(new Event('change'));
                }
            }''')
            page.wait_for_timeout(3000)
        except Exception as e:
            print("⚠️ Ошибка выбора года:", e)
            
        # Выбираем категорию "Трудовые споры" (код: 142030000100000000)
        print("📂 Выбираем категорию 'Трудовые споры'...")
        try:
            page.evaluate('''() => {
                var select = document.querySelector("select[name$='edit-category']");
                if (select && select.selectize) {
                    select.selectize.setValue("142030000100000000");
                } else if (select) {
                    select.value = "142030000100000000";
                    select.dispatchEvent(new Event('change'));
                }
            }''')
            page.wait_for_timeout(2000)
        except Exception as e:
            print("⚠️ Ошибка выбора категории:", e)
            
        # Запускаем поиск
        print("🔎 Нажимаем 'Искать'...")
        try:
            page.evaluate('''() => {
                var btn = document.querySelector("input[value='Искать по заданным параметрами']") || 
                          document.querySelector("input.button-primary[type='submit']");
                if (btn) btn.click();
            }''')
            page.wait_for_timeout(7000)
        except Exception as e:
            print("❌ Ошибка клика по кнопке поиска:", e)
            browser.close()
            return False
            
        # Цикл по страницам пагинации
        for page_num in range(1, max_pages + 1):
            print(f"\n📄 Парсинг страницы {page_num}...")
            
            # Находим строки таблицы
            rows = page.locator("div[id$='lawsuitPanel'] table tbody tr[onclick^='viewSelectedLawsuit']").all()
            if not rows:
                print("⚠️ Строки таблицы не найдены.")
                break
                
            print(f"Найдено {len(rows)} дел на странице.")
            
            # Парсим дела на текущей странице
            for row in rows:
                try:
                    cells = row.locator("td").all()
                    if len(cells) < 5:
                        continue
                        
                    # Номер и тип дела
                    num_type_html = cells[0].inner_html()
                    paragraphs = cells[0].locator("p").all()
                    case_number = paragraphs[0].inner_text().strip() if len(paragraphs) > 0 else "Не указан"
                    case_type = paragraphs[2].inner_text().strip() if len(paragraphs) > 2 else "Гражданское дело"
                    
                    # Стороны
                    parties = cells[1].inner_text().strip()
                    
                    # Суд
                    court = cells[2].inner_text().strip()
                    
                    # Результат
                    result = cells[3].inner_text().strip()
                    
                    # Категория
                    category = cells[4].inner_text().strip()
                    
                    case_data = {
                        "case_number": case_number,
                        "case_type": case_type,
                        "parties": parties,
                        "court": court,
                        "result": result,
                        "category": category,
                        "scraped_at": datetime.now().isoformat()
                    }
                    raw_cases.append(case_data)
                    
                    # Выделяем компанию и физлицо
                    entities = extract_entities(parties)
                    company = entities["company"]
                    person = entities["person"]
                    
                    if company and company != "Не указано":
                        city = normalize_city(court)
                        lead_data = {
                            "company_name": company,
                            "name": person,
                            "phone": "Не указан",
                            "email": "Не указан",
                            "source": "office.sud.kz",
                            "query": "Трудовые споры",
                            "city": city,
                            "url": "https://office.sud.kz/form/courtActs/index.xhtml",
                            "court_result": result,
                            "case_number": case_number
                        }
                        court_leads.append(lead_data)
                        print(f"  🏢 Лид: {company} | 👤 {person} | ⚖️ {result}")
                        
                except Exception as ex:
                    print(f"⚠️ Ошибка парсинга строки: {ex}")
                    
            if page_num < max_pages:
                # Переходим на следующую страницу
                first_case_locator = page.locator("div[id$='lawsuitPanel'] table tbody tr[onclick^='viewSelectedLawsuit'] td:first-child p:first-child")
                if first_case_locator.count() > 0:
                    old_first_case = first_case_locator.first.inner_text().strip()
                else:
                    old_first_case = ""
                    
                next_button = page.locator("a:has-text('►')")
                if next_button.count() > 0:
                    print("➡️ Переходим на следующую страницу...")
                    next_button.first.click()
                    
                    # Ждем смены первого дела на странице
                    try:
                        page.wait_for_function(
                            f"""() => {{
                                const el = document.querySelector("div[id$='lawsuitPanel'] table tbody tr[onclick^='viewSelectedLawsuit'] td:first-child p:first-child");
                                return el && el.innerText.trim() !== '{old_first_case}';
                            }}""",
                            timeout=8000
                        )
                        page.wait_for_timeout(2000) # дополнительная пауза
                    except Exception:
                        print("⚠️ Таймаут ожидания обновления страницы. Продолжаем.")
                        page.wait_for_timeout(3000)
                else:
                    print("🛑 Кнопка следующей страницы не найдена. Сбор завершен.")
                    break
                    
        browser.close()
        
    # Сохраняем сырые данные судебных дел
    raw_json_file = f"{output_dir}/court_cases_raw.json"
    with open(raw_json_file, "w", encoding="utf-8") as f:
        json.dump(raw_cases, f, ensure_ascii=False, indent=2)
        
    raw_csv_file = f"{output_dir}/court_cases_raw.csv"
    with open(raw_csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["case_number", "case_type", "parties", "court", "result", "category", "scraped_at"])
        writer.writeheader()
        writer.writerows(raw_cases)
        
    # Сохраняем извлеченные B2B лиды для ИИ-обогащения
    court_leads_file = "06_Scripts_and_Tools/court_leads.json"
    with open(court_leads_file, "w", encoding="utf-8") as f:
        json.dump(court_leads, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 Сбор судебных дел завершен!")
    print(f"Собрано сырых дел: {len(raw_cases)}")
    print(f"Извлечено потенциальных B2B-лидов: {len(court_leads)}")
    print(f"Файлы сохранены в {output_dir} и {court_leads_file}")
    return True

if __name__ == "__main__":
    import sys
    success = parse_labor_cases(max_pages=5)
    if not success:
        sys.exit(1)
