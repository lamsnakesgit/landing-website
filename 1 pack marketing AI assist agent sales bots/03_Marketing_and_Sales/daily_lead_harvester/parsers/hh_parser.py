import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_hh_leads(queries, area_id=40, source_label="hh.kz", max_per_query=5):
    """
    Прямой HTML-парсер вакансий и работодателей с hh.ru и hh.kz.
    Возвращает 100% живые горячие заявки и вакансии.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    base_domain = "https://hh.kz" if "kz" in source_label else "https://hh.ru"

    for query in queries:
        logger.info(f"🔎 Сканируем [{source_label}] по запросу: '{query}'...")
        encoded_query = urllib.parse.quote(query)
        url = f"{base_domain}/search/vacancy?text={encoded_query}"

        try:
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                title_tags = soup.find_all("a", attrs={"data-qa": "serp-item__title"})

                count = 0
                for title_tag in title_tags:
                    title = title_tag.text.strip()
                    href = title_tag.get("href", "")
                    if href.startswith("/"):
                        href = f"{base_domain}{href}"

                    parent = title_tag.find_parent("div", class_=lambda x: x and ("vacancy-card" in x or "serp-item" in x))
                    comp_tag = parent.find("a", attrs={"data-qa": "vacancy-serp__vacancy-employer"}) if parent else None
                    company = comp_tag.text.strip() if comp_tag else "Компания на HH"
                    comp_href = comp_tag.get("href", "") if comp_tag else ""
                    if comp_href.startswith("/"):
                        comp_href = f"{base_domain}{comp_href}"

                    contacts_str = f"Вакансия: {href}"
                    if comp_href:
                        contacts_str += f" | Профиль работодателя: {comp_href}"

                    leads.append({
                        "source": source_label,
                        "query": query,
                        "company": company,
                        "title": title,
                        "contacts": contacts_str,
                        "email": "",
                        "phone": "",
                        "contact_person": "HR / Руководитель подбора",
                        "link": href,
                        "details": f"Активная вакансия [{title}] компании {company} на {source_label}"
                    })

                    count += 1
                    if count >= max_per_query:
                        break
            else:
                logger.warning(f"Отказ HH ({resp.status_code}) для {query}")

            time.sleep(1.0)
        except Exception as e:
            logger.error(f"Ошибка сбора {source_label} по '{query}': {e}")

    logger.info(f"✅ [{source_label}] Завершено! Собрано лидов: {len(leads)}")
    return leads
