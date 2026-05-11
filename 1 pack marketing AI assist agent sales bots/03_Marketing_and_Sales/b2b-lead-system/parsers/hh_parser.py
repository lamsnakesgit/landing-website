"""
hh.kz Parser — вакансии, компании, контакты
Запуск: python hh_parser.py --city Алматы --sphere IT --role "директор"
"""

import httpx
import asyncio
import argparse
import json
import re
import time
import logging
from typing import Optional
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HH_API = "https://api.hh.ru"

AREA_MAP = {
    "алматы": "160",
    "астана": "159",
    "шымкент": "202",
    "актау": "167",
    "атырау": "168",
    "казахстан": "40",  # вся страна
}

HEADERS = {
    "User-Agent": "b2b-lead-parser/1.0 (contact: your@email.com)",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "HH-User-Agent": "b2b-lead-parser/1.0",
}


def get_area_id(city: str) -> str:
    return AREA_MAP.get(city.lower(), "40")


async def fetch_vacancies(
    client: httpx.AsyncClient,
    city: str,
    sphere: str,
    role: str,
    page: int = 0,
    per_page: int = 50
) -> dict:
    area_id = get_area_id(city)
    params = {
        "text": f"{role} {sphere}",
        "area": area_id,
        "per_page": per_page,
        "page": page,
        "order_by": "publication_time",
        "search_field": "name",  # ищем в названии должности
    }
    resp = await client.get(f"{HH_API}/vacancies", params=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


async def fetch_vacancy_detail(client: httpx.AsyncClient, vacancy_id: str) -> dict:
    resp = await client.get(f"{HH_API}/vacancies/{vacancy_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


async def fetch_employer(client: httpx.AsyncClient, employer_id: str) -> dict:
    resp = await client.get(f"{HH_API}/employers/{employer_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


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


def clean_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:1000]


async def parse_hh(city: str, sphere: str, role: str, max_pages: int = 5) -> dict:
    companies = {}
    vacancies = []
    contacts = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(max_pages):
            log.info(f"hh.kz — страница {page + 1}/{max_pages}")
            try:
                data = await fetch_vacancies(client, city, sphere, role, page=page)
            except Exception as e:
                log.error(f"Ошибка при получении страницы {page}: {e}")
                break

            items = data.get("items", [])
            if not items:
                break

            tasks = [fetch_vacancy_detail(client, v["id"]) for v in items]
            details = await asyncio.gather(*tasks, return_exceptions=True)

            for item, detail in zip(items, details):
                if isinstance(detail, Exception):
                    log.warning(f"Пропуск вакансии {item.get('id')}: {detail}")
                    continue

                emp = detail.get("employer", {})
                emp_id = str(emp.get("id", ""))
                if not emp_id:
                    continue

                # --- Компания ---
                if emp_id not in companies:
                    try:
                        emp_detail = await fetch_employer(client, emp_id)
                        site = emp_detail.get("site_url") or emp_detail.get("alternate_url", "")
                        description_raw = emp_detail.get("description", "")
                        description = clean_html(description_raw)
                        emp_email = extract_email(description_raw)
                        emp_phone = extract_phone(description_raw)
                        area = emp_detail.get("area", {}).get("name", city)
                        industries = [i.get("name", "") for i in emp_detail.get("industries", [])]
                    except Exception as e:
                        log.warning(f"Ошибка получения работодателя {emp_id}: {e}")
                        site = emp.get("alternate_url", "")
                        description = ""
                        emp_email = None
                        emp_phone = None
                        area = city
                        industries = []

                    companies[emp_id] = {
                        "id": emp_id,
                        "name": emp.get("name", ""),
                        "site": site,
                        "email": emp_email,
                        "phone": emp_phone,
                        "city": area,
                        "description": description,
                        "category": ", ".join(industries) if industries else sphere,
                        "source": "hh.kz",
                        "hh_url": emp.get("alternate_url", ""),
                        "employee_count_range": emp.get("employer_type", ""),
                    }
                    await asyncio.sleep(0.3)

                # --- Вакансия ---
                desc_raw = detail.get("description", "")
                salary = detail.get("salary") or {}
                salary_str = ""
                if salary:
                    fr = salary.get("from")
                    to = salary.get("to")
                    curr = salary.get("currency", "")
                    salary_str = f"{fr or ''}-{to or ''} {curr}".strip("- ")

                vacancies.append({
                    "company_id": emp_id,
                    "vacancy_id": detail.get("id"),
                    "title": detail.get("name", ""),
                    "description": clean_html(desc_raw),
                    "url": detail.get("alternate_url", ""),
                    "salary": salary_str,
                    "city": detail.get("area", {}).get("name", city),
                    "published_at": detail.get("published_at", ""),
                    "experience": detail.get("experience", {}).get("name", ""),
                    "employment": detail.get("employment", {}).get("name", ""),
                    "source": "hh.kz",
                })

                # --- Контакт ---
                contact_info = detail.get("contacts", {})
                if contact_info:
                    c_name = contact_info.get("name", "")
                    c_email = contact_info.get("email", "")
                    c_phones = contact_info.get("phones", [])
                    c_phone = c_phones[0].get("formatted", "") if c_phones else ""
                    if c_name or c_email or c_phone:
                        contacts.append({
                            "company_id": emp_id,
                            "vacancy_id": str(detail.get("id", "")),
                            "name": c_name,
                            "role": detail.get("name", ""),
                            "email": c_email,
                            "phone": c_phone,
                            "contact_link": detail.get("alternate_url", ""),
                            "source": "hh.kz",
                        })

                # Проверяем email/телефон в тексте вакансии
                desc_email = extract_email(desc_raw)
                desc_phone = extract_phone(desc_raw)
                if desc_email or desc_phone:
                    contacts.append({
                        "company_id": emp_id,
                        "vacancy_id": str(detail.get("id", "")),
                        "name": "",
                        "role": detail.get("name", ""),
                        "email": desc_email or "",
                        "phone": desc_phone or "",
                        "contact_link": detail.get("alternate_url", ""),
                        "source": "hh.kz (из описания)",
                    })

            total_pages = data.get("pages", 1)
            if page >= total_pages - 1:
                break
            await asyncio.sleep(1)

    return {
        "companies": list(companies.values()),
        "vacancies": vacancies,
        "contacts": contacts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hh.kz B2B Parser")
    parser.add_argument("--city", default="Алматы")
    parser.add_argument("--sphere", default="IT")
    parser.add_argument("--role", default="директор")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--output", default="hh_result.json")
    args = parser.parse_args()

    result = asyncio.run(parse_hh(args.city, args.sphere, args.role, args.pages))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    log.info(f"Готово: {len(result['companies'])} компаний, {len(result['vacancies'])} вакансий, {len(result['contacts'])} контактов")
    log.info(f"Результат сохранён в {args.output}")
