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


async def search_adata(city: str, sphere: str, role: str, max_pages: int = 3) -> dict:
    """
    adata.kz (pk.adata.kz) — поиск по казахстанским компаниям и бизнесам.
    Используем поисковый фоллбэк (DuckDuckGo Lite + Tavily) по pk.adata.kz для надежного получения реестра.
    """
    import urllib.parse
    companies = {}
    vacancies = []
    contacts = []

    query = f"{sphere} {role}".strip()
    log.info(f"adata.kz (pk.adata.kz) — поиск компаний по запросу: '{query}'")

    # Ищем компании через DuckDuckGo Lite по pk.adata.kz
    ddg_url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"q": f"site:pk.adata.kz {query} {city}"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(ddg_url, headers=headers, data=data)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.find_all('a', class_='result-link')
                
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    decoded_href = urllib.parse.unquote(href)
                    
                    match_url = re.search(r"https?://pk\.adata\.kz/company/\d+", decoded_href)
                    if match_url:
                        comp_url = match_url.group(0)
                        bin_match = re.search(r"/company/(\d+)", comp_url)
                        bin_code = bin_match.group(1) if bin_match else ""
                        
                        snippet = ""
                        tr = link.find_parent('tr')
                        if tr:
                            next_tr = tr.find_next_sibling('tr')
                            if next_tr:
                                snip_td = next_tr.select_one('.result-snippet')
                                if snip_td:
                                    snippet = snip_td.get_text(strip=True)
                                    
                        comp_name = title.replace("- adata.kz", "").replace("– adata.kz", "").strip()
                        
                        comp_id = f"adata_{bin_code}" if bin_code else comp_name
                        if comp_id not in companies:
                            phone = extract_phone(snippet) or ""
                            email = extract_email(snippet) or ""
                            
                            companies[comp_id] = {
                                "id": comp_id,
                                "name": comp_name,
                                "bin": bin_code,
                                "inn": bin_code,
                                "site": comp_url,
                                "phone": phone,
                                "email": email,
                                "city": city,
                                "description": snippet,
                                "category": sphere,
                                "source": "adata.kz",
                                "hh_url": comp_url,
                            }
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
