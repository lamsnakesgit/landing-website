"""
Goszakup.gov.kz Parser — Реестр поставщиков, поиск ЛПР и мобильных телефонов.
Запуск: python goszakup_parser.py --keyword "разработка"
"""

import asyncio
import json
import argparse
import logging
import re
from playwright.async_api import async_playwright
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def extract_mobile_phone(text: str) -> str:
    """Извлекает мобильные номера (фильтрует городские)"""
    if not text:
        return ""
    # Ищем номера начинающиеся с +7 7, 8 7
    matches = re.findall(r"(?:\+7|8)[\s\-]?\(?7\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    if matches:
        return matches[0]
    return ""

async def parse_goszakup(keyword: str, max_pages: int = 1) -> Dict[str, List[dict]]:
    companies = []
    contacts = []
    
    log.info(f"Запуск парсера Госзакупок по ключевому слову: '{keyword}'")
    
    # Используем видимый режим для обхода защиты
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        try:
            # Открываем реестр поставщиков
            url = f"https://www.goszakup.gov.kz/ru/registry/show_supplier?count_record=50&name_ru={keyword}"
            log.info(f"Открываем URL: {url}")
            await page.goto(url, timeout=60000)
            
            # Ждем загрузки таблицы
            await page.wait_for_selector("table.table-bordered", timeout=15000)
            
            for page_num in range(1, max_pages + 1):
                log.info(f"Госзакупки — Обработка страницы {page_num}")
                
                rows = await page.query_selector_all("table.table-bordered tbody tr")
                log.info(f"Найдено строк: {len(rows)}")
                
                for row in rows:
                    cols = await row.query_selector_all("td")
                    if len(cols) < 5:
                        continue
                        
                    bin_inn = await cols[1].inner_text()
                    name = await cols[2].inner_text()
                    name = name.strip()
                    
                    # Проваливаемся в карточку (ссылка обычно во второй или третьей колонке)
                    link_element = await cols[2].query_selector("a")
                    profile_url = ""
                    if link_element:
                        profile_url = await link_element.get_attribute("href")
                        
                    company = {
                        "id": f"gz_{bin_inn.strip()}",
                        "name": name,
                        "bin": bin_inn.strip(),
                        "source": "goszakup",
                        "city": "Казахстан",
                        "category": keyword,
                        "hh_url": profile_url or url
                    }
                    
                    # Если есть ссылка на профиль, собираем детальные контакты
                    lpr_name = ""
                    phone = ""
                    email = ""
                    
                    if profile_url:
                        # Открываем новую вкладку для карточки, чтобы не сбивать пагинацию
                        detail_page = await context.new_page()
                        try:
                            await detail_page.goto(profile_url, timeout=15000)
                            text_content = await detail_page.inner_text("body")
                            
                            # Поиск ФИО руководителя
                            fio_match = re.search(r"ФИО руководителя[:\n\s]+([А-Яа-яЁё\s]+)", text_content)
                            if fio_match:
                                lpr_name = fio_match.group(1).strip()
                                
                            # Поиск телефона
                            phone_match = re.search(r"Телефон[:\n\s]+([\d\+\-\(\)\s]+)", text_content)
                            if phone_match:
                                raw_phone = phone_match.group(1).strip()
                                mobile = extract_mobile_phone(raw_phone)
                                phone = mobile if mobile else raw_phone
                                
                            # Поиск Email
                            email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text_content)
                            if email_match:
                                email = email_match.group(0)
                                
                        except Exception as e:
                            log.debug(f"Ошибка загрузки профиля {profile_url}: {e}")
                        finally:
                            await detail_page.close()
                    
                    company["email"] = email
                    company["phone"] = phone
                    
                    companies.append(company)
                    
                    if lpr_name or phone or email:
                        contacts.append({
                            "company_id": company["id"],
                            "name": lpr_name or "Руководитель",
                            "role": "Руководитель / ИП",
                            "email": email,
                            "phone": phone,
                            "contact_link": profile_url or url,
                            "source": "goszakup"
                        })
                
                # Попытка перехода на следующую страницу
                next_btn = await page.query_selector("ul.pagination li.next a")
                if next_btn and page_num < max_pages:
                    await next_btn.click()
                    await page.wait_for_timeout(3000)
                else:
                    break
                    
        except Exception as e:
            log.error(f"Ошибка парсинга Госзакупок: {e}")
        finally:
            await browser.close()
            
    return {
        "companies": companies,
        "contacts": contacts,
        "vacancies": [] # Заглушка для совместимости
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="разработка", help="Ключевое слово")
    parser.add_argument("--pages", type=int, default=1, help="Кол-во страниц")
    parser.add_argument("--output", default="goszakup_result.json", help="Куда сохранить")
    args = parser.parse_args()
    
    result = asyncio.run(parse_goszakup(args.keyword, args.pages))
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    log.info(f"Сохранено {len(result['companies'])} компаний и {len(result['contacts'])} контактов.")
