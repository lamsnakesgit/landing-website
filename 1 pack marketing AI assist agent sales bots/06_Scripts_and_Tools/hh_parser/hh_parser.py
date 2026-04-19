import time
import requests
from loguru import logger
import csv
import os

# Ensure logs dir exists
os.makedirs("logs", exist_ok=True)
# Configure logging to save to a file as per clinerules
logger.add("logs/hh_parser.log", rotation="10 MB", retention="7 days", level="INFO")

HH_API_URL = "https://api.hh.ru/vacancies"

def get_companies_hiring(text_query="Руководитель отдела продаж", area=40, per_page=100, num_pages=2):
    """
    Search HH.ru for vacancies and extract distinct companies hiring.
    area=40 is Kazakhstan (160 is Almaty).
    """
    logger.info(f"Начинаем парсинг HH.ru по запросу: '{text_query}', регион: {area}")
    
    companies = {}
    
    for page in range(num_pages):
        params = {
            "text": text_query,
            "area": area,
            "per_page": per_page,
            "page": page
        }
        
        headers = {
            "User-Agent": "AIAgentOutreach/1.0 (info@aiconicvibe.store)"
        }
        
        try:
            response = requests.get(HH_API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                logger.info("Больше нет вакансий")
                break
                
            for item in items:
                employer = item.get("employer", {})
                emp_id = employer.get("id")
                emp_name = employer.get("name")
                emp_url = employer.get("alternate_url")
                
                vac_name = item.get("name")
                vac_url = item.get("alternate_url")
                
                if emp_id and emp_id not in companies:
                    companies[emp_id] = {
                        "company_name": emp_name,
                        "employer_url": emp_url,
                        "vacancy_name": vac_name,
                        "vacancy_url": vac_url,
                        "source": "hh.ru"
                    }
                    
            logger.info(f"Страница {page+1} обработана. Найдено компаний нарастающим итогом: {len(companies)}")
            time.sleep(1) # Be polite according to HH limits
            
        except Exception as e:
            logger.error(f"Ошибка при запросе HH.ru: {e}")
            break

    logger.info(f"Парсинг окончен. Всего уникальных компаний: {len(companies)}")
    return list(companies.values())

def save_to_csv(data, filename="leads_hh.csv"):
    if not data:
        logger.warning("Нет данных для сохранения")
        return
        
    keys = data[0].keys()
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Данные сохранены в {filename}")
    except Exception as e:
        logger.error(f"Ошибка сохранения CSV: {e}")

if __name__ == "__main__":
    # ==========================================
    # ⚙️ НАСТРОЙКИ ПАРСЕРА
    # ==========================================
    # Коды популярных городов (Area ID из базы HH.ru):
    # 1 - Москва
    # 2 - Санкт-Петербург
    # 1220 - Екатеринбург
    # 40 - Весь Казахстан
    # 160 - Алматы
    # 71 - Астана
    # ==========================================
    
    CITY_CODE = 1220  # <-- МЕНЯЙ ГОРОД ТУТ (например, Екатеринбург)
    SEARCH_QUERY = "Руководитель отдела продаж OR Коммерческий директор" # <-- МЕНЯЙ ЗАПРОС ТУТ
    PAGES_TO_PARSE = 2 # Количество страниц для сбора
    
    results = get_companies_hiring(text_query=SEARCH_QUERY, area=CITY_CODE, num_pages=PAGES_TO_PARSE)
    
    save_to_csv(results, "hh_leads.csv")
    print(f"Парсинг завершен! Найдено уникальных B2B компаний: {len(results)}. Файл: hh_leads.csv")
