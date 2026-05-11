"""
adata.kz Parser — вакансии и компании Казахстана
Запуск: python adata_parser.py --city Алматы --sphere "маркетинг" --role "руководитель"
"""

import httpx
import asyncio
import argparse
import json
import re
import logging
from typing import Optional
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://www.adata.kz"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Referer": "https://www.adata.kz",
}

# Маппинг городов
CITY_MAP = {
    "алматы": "almaty",
    "астана": "astana",
    "нур-султан": "astana",
    "шымкент": "shymkent",
    "актобе": "aktobe",
    "атырау": "atyrau",
}


def get_city_slug(city: str) -> str:
    return CITY_MAP.get(city.lower(), "almaty")


def extract_email(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"[\+7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    return match.group(0) if match else None


async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(url, headers=HEADERS, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


async def parse_company_page(client: httpx.AsyncClient, company_url: str, city: str, sphere: str) -> Optional[dict]:
    """Парсит страницу компании на adata.kz"""
    try:
        html = await fetch_page(client, company_url)
        soup = BeautifulSoup(html, "html.parser")

        name_el = soup.select_one("h1.company-name, h1.title, .org-name h1")
        name = name_el.get_text(strip=True) if name_el else ""

        phone_el = soup.select_one(".phone, .contact-phone, [itemprop='telephone']")
        phone = phone_el.get_text(strip=True) if phone_el else ""

        email_el = soup.select_one(".email, [itemprop='email'], a[href^='mailto:']")
        email = ""
        if email_el:
            email = email_el.get("href", "").replace("mailto:", "") or email_el.get_text(strip=True)

        site_el = soup.select_one(".website a, [itemprop='url'], a[rel='nofollow'][href^='http']")
        site = site_el.get("href", "") if site_el else ""

        desc_el = soup.select_one(".description, .about-company, [itemprop='description']")
        description = desc_el.get_text(strip=True)[:500] if desc_el else ""

        full_text = soup.get_text()
        if not phone:
            phone = extract_phone(full_text) or ""
        if not email:
            email = extract_email(full_text) or ""

        if not name:
            return None

        return {
            "name": name,
            "site": site,
            "phone": phone,
            "email": email,
            "city": city,
            "description": description,
            "category": sphere,
            "source": "adata.kz",
            "hh_url": company_url,
        }
    except Exception as e:
        log.warning(f"Ошибка парсинга {company_url}: {e}")
        return None


async def search_adata(city: str, sphere: str, role: str, max_pages: int = 5) -> dict:
    """
    adata.kz — поиск по вакансиям и компаниям.
    Стратегия: используем поиск по каталогу компаний + фильтрация по городу.
    """
    companies = {}
    vacancies = []
    contacts = []

    city_slug = get_city_slug(city)
    query = f"{role} {sphere}".strip()

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, max_pages + 1):
            # Поиск по вакансиям
            search_url = f"{BASE_URL}/vacancy/search/?text={query}&city={city_slug}&page={page}"
            log.info(f"adata.kz вакансии — страница {page}: {search_url}")

            try:
                html = await fetch_page(client, search_url)
                soup = BeautifulSoup(html, "html.parser")

                # Ищем карточки вакансий
                vacancy_cards = soup.select(".vacancy-card, .vacancy-item, article.vacancy, .job-item")
                if not vacancy_cards:
                    # Fallback: ищем ссылки на вакансии
                    vacancy_cards = soup.select("a[href*='/vacancy/']")

                if not vacancy_cards:
                    log.info(f"Нет результатов на странице {page}")
                    break

                for card in vacancy_cards:
                    try:
                        # Название вакансии
                        title_el = card.select_one("h2, h3, .title, .vacancy-title, a.vacancy-name")
                        title = title_el.get_text(strip=True) if title_el else ""

                        if not title and card.name == "a":
                            title = card.get_text(strip=True)

                        # Ссылка
                        link_el = card.select_one("a") if card.name != "a" else card
                        href = link_el.get("href", "") if link_el else ""
                        vacancy_url = BASE_URL + href if href.startswith("/") else href

                        # Компания
                        company_el = card.select_one(".company-name, .employer, .org-name")
                        company_name = company_el.get_text(strip=True) if company_el else ""

                        # Зарплата
                        salary_el = card.select_one(".salary, .wage")
                        salary = salary_el.get_text(strip=True) if salary_el else ""

                        # Город
                        city_el = card.select_one(".city, .location, .address")
                        card_city = city_el.get_text(strip=True) if city_el else city

                        vac_id = href.strip("/").split("/")[-1] if href else ""
                        comp_key = company_name or f"adata_{vac_id}"

                        if comp_key not in companies:
                            companies[comp_key] = {
                                "id": comp_key,
                                "name": company_name,
                                "site": "",
                                "phone": "",
                                "email": "",
                                "city": card_city,
                                "description": "",
                                "category": sphere,
                                "source": "adata.kz",
                                "hh_url": "",
                            }

                        if vac_id:
                            vacancies.append({
                                "company_id": comp_key,
                                "vacancy_id": f"adata_{vac_id}",
                                "title": title,
                                "description": "",
                                "url": vacancy_url,
                                "salary": salary,
                                "city": card_city,
                                "published_at": "",
                                "source": "adata.kz",
                            })

                    except Exception as e:
                        log.warning(f"Ошибка обработки карточки: {e}")
                        continue

            except Exception as e:
                log.error(f"Ошибка получения страницы {page} adata.kz: {e}")
                break

            await asyncio.sleep(1.5)

        # Поиск по каталогу компаний
        log.info("adata.kz — поиск по каталогу компаний...")
        try:
            catalog_url = f"{BASE_URL}/company/search/?text={query}&city={city_slug}"
            html = await fetch_page(client, catalog_url)
            soup = BeautifulSoup(html, "html.parser")

            company_links = soup.select("a[href*='/company/']")
            seen_links = set()
            for link in company_links[:30]:  # первые 30 компаний
                href = link.get("href", "")
                if "/company/" not in href or href in seen_links:
                    continue
                seen_links.add(href)
                company_url = BASE_URL + href if href.startswith("/") else href
                comp_data = await parse_company_page(client, company_url, city, sphere)
                if comp_data:
                    key = comp_data["name"]
                    if key not in companies:
                        comp_data["id"] = key
                        companies[key] = comp_data
                await asyncio.sleep(0.8)

        except Exception as e:
            log.warning(f"Каталог компаний adata.kz: {e}")

    return {
        "companies": list(companies.values()),
        "vacancies": vacancies,
        "contacts": contacts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="adata.kz B2B Parser")
    parser.add_argument("--city", default="Алматы")
    parser.add_argument("--sphere", default="маркетинг")
    parser.add_argument("--role", default="директор")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--output", default="adata_result.json")
    args = parser.parse_args()

    result = asyncio.run(search_adata(args.city, args.sphere, args.role, args.pages))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    log.info(f"Готово: {len(result['companies'])} компаний, {len(result['vacancies'])} вакансий")
