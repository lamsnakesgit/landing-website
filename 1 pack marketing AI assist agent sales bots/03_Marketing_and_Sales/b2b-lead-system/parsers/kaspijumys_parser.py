"""
Каспи Жұмыс / jobs.kaspi.kz Parser — вакансии Казахстана
Запуск: python kaspijumys_parser.py --city Алматы --query "маркетолог" --pages 3
"""
import httpx
import asyncio
import argparse
import json
import re
import logging
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://jobs.kaspi.kz"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,kk-KZ,kk;q=0.8",
    "Referer": "https://jobs.kaspi.kz",
}


def extract_email(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    # Казахстанские номера: +7 7xx xxx xx xx, 8 7xx xxx xx xx, +7(7xx)xxx-xx-xx
    patterns = [
        r"\+7\s?7\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",
        r"\+7\s?\(?7\d{2}\)?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
        r"8\s?7\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",
        r"8\s?\(?7\d{2}\)?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(url, headers=HEADERS, follow_redirects=True, timeout=30.0)
    resp.raise_for_status()
    return resp.text


async def parse_vacancy_detail(client: httpx.AsyncClient, vacancy_url: str) -> dict:
    """Парсит детальную страницу вакансии на Каспи Жұмыс"""
    try:
        html = await fetch_page(client, vacancy_url)
        soup = BeautifulSoup(html, "html.parser")

        # Описание вакансии
        desc_el = soup.select_one("[data-test-id='vacancy-description'], .vacancy-description, .job-description, [class*='description']")
        description = desc_el.get_text(strip=True)[:1000] if desc_el else ""

        # Контакты в описании
        email = extract_email(description) or ""
        phone = extract_phone(description) or ""

        # Контактное лицо
        contact_el = soup.select_one("[data-test-id='vacancy-contact'], .contact-name, .recruiter-name")
        contact_name = contact_el.get_text(strip=True) if contact_el else ""

        # Требования / обязанности
        req_el = soup.select_one("[data-test-id='vacancy-requirements'], .requirements")
        requirements = req_el.get_text(strip=True)[:500] if req_el else ""

        return {
            "description": description,
            "requirements": requirements,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
        }
    except Exception as e:
        log.warning(f"Ошибка парсинга деталей вакансии {vacancy_url}: {e}")
        return {
            "description": "",
            "requirements": "",
            "contact_name": "",
            "email": "",
            "phone": "",
        }


async def search_kaspi(city: str, query: str, max_pages: int = 3) -> dict:
    """
    Каспи Жұмыс — поиск вакансий.
    Стратегия: ищем по тексту, собираем карточки вакансий и детали.
    """
    companies = {}
    vacancies = []
    contacts = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, max_pages + 1):
            # Параметры поиска
            search_url = f"{BASE_URL}/search"
            params = {
                "query": query,
                "page": page,
            }
            # Если город указан и это не "все", можно добавить фильтр
            # Каспи использует region параметр, но пока ищем по всему Казахстану
            if city and city.lower() not in ("все", "казахстан", "вся страна"):
                params["region"] = city

            log.info(f"Каспи Жұмыс — страница {page}: {search_url} (query={query})")

            try:
                html = await fetch_page(client, search_url + "?" + "&".join(f"{k}={v}" for k, v in params.items()))
                soup = BeautifulSoup(html, "html.parser")

                # Ищем карточки вакансий — адаптируем под актуальную структуру Каспи
                vacancy_cards = soup.select(
                    "[data-test-id='vacancy-card'], .vacancy-card, .job-card, "
                    "a[href*='/vacancy/'], a[href*='/job/']"
                )

                if not vacancy_cards:
                    # Fallback: ищем любые ссылки на вакансии
                    vacancy_cards = soup.find_all("a", href=re.compile(r"/(vacancy|job)/\d+"))

                if not vacancy_cards:
                    log.info(f"Нет результатов на странице {page}")
                    break

                for card in vacancy_cards:
                    try:
                        # Ссылка на вакансию
                        href = card.get("href", "") if card.name == "a" else ""
                        if not href:
                            link_el = card.select_one("a[href*='/vacancy/'], a[href*='/job/']")
                            if link_el:
                                href = link_el.get("href", "")

                        if not href:
                            continue

                        vacancy_url = urljoin(BASE_URL, href)
                        vac_id = href.strip("/").split("/")[-1].split("?")[0]

                        # Название вакансии
                        title_el = card.select_one(
                            "[data-test-id='vacancy-title'], .vacancy-title, h2, h3, .title, .job-title"
                        ) or (card if card.name == "a" else None)
                        title = title_el.get_text(strip=True) if title_el else ""

                        # Компания
                        company_el = card.select_one(
                            "[data-test-id='company-name'], .company-name, .employer-name, .org-name"
                        )
                        company_name = company_el.get_text(strip=True) if company_el else ""

                        # Зарплата
                        salary_el = card.select_one(
                            "[data-test-id='salary'], .salary, .wage, .compensation"
                        )
                        salary = salary_el.get_text(strip=True) if salary_el else ""

                        # Город
                        city_el = card.select_one(
                            "[data-test-id='city'], .city, .location, .address"
                        )
                        card_city = city_el.get_text(strip=True) if city_el else city

                        # --- Детали вакансии ---
                        details = await parse_vacancy_detail(client, vacancy_url)

                        comp_key = company_name or f"kaspi_{vac_id}"

                        # Создаём запись компании
                        if comp_key not in companies:
                            companies[comp_key] = {
                                "id": comp_key,
                                "name": company_name,
                                "site": "",
                                "phone": details.get("phone", ""),
                                "email": details.get("email", ""),
                                "city": card_city,
                                "description": details.get("description", "")[:500],
                                "category": query,
                                "source": "kaspi.jobs",
                                "hh_url": vacancy_url,
                            }

                        # Вакансия
                        vacancies.append({
                            "company_id": comp_key,
                            "vacancy_id": f"kaspi_{vac_id}",
                            "title": title,
                            "description": details.get("description", ""),
                            "url": vacancy_url,
                            "salary": salary,
                            "city": card_city,
                            "published_at": "",
                            "source": "kaspi.jobs",
                        })

                        # Контакт из деталей
                        if details.get("email") or details.get("phone") or details.get("contact_name"):
                            contacts.append({
                                "company_id": comp_key,
                                "vacancy_id": f"kaspi_{vac_id}",
                                "name": details.get("contact_name", ""),
                                "role": title,
                                "email": details.get("email", ""),
                                "phone": details.get("phone", ""),
                                "contact_link": vacancy_url,
                                "source": "kaspi.jobs",
                            })

                        await asyncio.sleep(0.5)  # Не дудосим

                    except Exception as e:
                        log.warning(f"Ошибка обработки карточки Каспи: {e}")
                        continue

            except Exception as e:
                log.error(f"Ошибка получения страницы {page} Каспи Жұмыс: {e}")
                break

            await asyncio.sleep(1.5)

    return {
        "companies": list(companies.values()),
        "vacancies": vacancies,
        "contacts": contacts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Каспи Жұмыс B2B Parser")
    parser.add_argument("--city", default="Алматы")
    parser.add_argument("--query", default="маркетолог")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--output", default="kaspi_result.json")
    args = parser.parse_args()

    result = asyncio.run(search_kaspi(args.city, args.query, args.pages))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    log.info(
        f"Готово: {len(result['companies'])} компаний, "
        f"{len(result['vacancies'])} вакансий, "
        f"{len(result['contacts'])} контактов"
    )