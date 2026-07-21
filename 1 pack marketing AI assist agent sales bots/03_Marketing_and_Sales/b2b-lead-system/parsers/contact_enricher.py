"""
Contact Enricher — обогащение контактов компаний
Заходит на сайт компании, ищет страницы контактов, извлекает email и телефоны.
Запуск: python contact_enricher.py --input leads.json --output leads_enriched.json
"""
import httpx
import asyncio
import argparse
import json
import re
import logging
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

# Пути к страницам контактов (приоритетный порядок)
CONTACT_PATHS = [
    "/contacts", "/contact", "/kontakty", "/kontakti",
    "/about/contacts", "/o-kompanii/kontakty",
    "/contact-us", "/contacts.html", "/contact.html",
    "/kontakty.html", "/kontakti.html",
]


def extract_email(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    # Казахстан / Россия / СНГ номера
    patterns = [
        r"\+7\s?7\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",  # KZ mobile
        r"\+7\s?\(?\d{3}\)?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",  # RU/KZ
        r"8\s?7\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",  # KZ 8-xxx
        r"8\s?\(?\d{3}\)?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",  # RU 8-xxx
        r"\+7\s?\d{3}\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",  # +7 XXX
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_telegram(text: str) -> Optional[str]:
    """Извлекает Telegram username или ссылку"""
    if not text:
        return None
    patterns = [
        r"t\.me/([a-zA-Z0-9_]{5,32})",
        r"telegram\.me/([a-zA-Z0-9_]{5,32})",
        r"telegram\.org/([a-zA-Z0-9_]{5,32})",
        r"@([a-zA-Z0-9_]{5,32})",  # Осторожно: может ловить лишнее
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            username = match.group(1)
            # Фильтруем очевидно невалидные
            if username.lower() not in ("example", "username", "test", "admin"):
                return f"https://t.me/{username}"
    return None


def extract_whatsapp(text: str) -> Optional[str]:
    """Извлекает WhatsApp ссылку или номер"""
    if not text:
        return None
    match = re.search(r"wa\.me/(\+?\d+)", text)
    if match:
        return f"https://wa.me/{match.group(1)}"
    return None


def normalize_url(url: str) -> Optional[str]:
    """Нормализует URL: добавляет https://, убирает trailing slash"""
    if not url:
        return None
    url = url.strip()
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        url = "https://" + url
    # Убираем trailing slash для единообразия
    return url.rstrip("/")


async def fetch_page(client: httpx.AsyncClient, url: str, timeout: float = 15.0) -> Optional[str]:
    try:
        resp = await client.get(url, headers=HEADERS, follow_redirects=True, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        log.debug(f"Ошибка загрузки {url}: {e}")
    return None


async def find_contact_page(client: httpx.AsyncClient, base_url: str) -> Optional[str]:
    """Ищет страницу контактов на сайте"""
    # Пробуем стандартные пути
    for path in CONTACT_PATHS:
        url = base_url + path
        try:
            resp = await client.head(url, headers=HEADERS, follow_redirects=True, timeout=10.0)
            if resp.status_code == 200:
                return url
        except Exception:
            continue

    # Если не нашли — парсим главную страницу и ищем ссылки
    try:
        html = await fetch_page(client, base_url, timeout=10.0)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        # Ищем ссылки с текстом "контакты", "связаться" и т.д.
        keywords = ["контакт", "связаться", "свяжитесь", "contact", "написать", "обратная связь"]
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True).lower()
            href = link.get("href", "")
            if any(kw in text for kw in keywords):
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    return full_url
    except Exception as e:
        log.debug(f"Ошибка поиска контактной страницы на {base_url}: {e}")

    return None


async def parse_contacts_from_page(html: str) -> Dict[str, List[str]]:
    """Извлекает все контакты из HTML-страницы"""
    soup = BeautifulSoup(html, "html.parser")

    # Убираем скрипты и стили
    for script in soup(["script", "style", "nav", "footer"]):
        script.decompose()

    text = soup.get_text(separator=" ", strip=True)

    # Извлекаем email'ы
    emails = set()
    # Из текста
    for match in re.finditer(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text):
        email = match.group(0)
        # Фильтруем типичные ложные срабатывания
        if not any(bad in email.lower() for bad in ["example", "test@", "admin@", "noreply", "no-reply", "info@example"]):
            emails.add(email)

    # Из mailto: ссылок
    for link in soup.find_all("a", href=re.compile(r"^mailto:")):
        href = link.get("href", "").replace("mailto:", "")
        if "@" in href and "example" not in href.lower():
            emails.add(href.split("?")[0])  # Убираем параметры

    # Извлекаем телефоны
    phones = set()
    phone_matches = re.finditer(
        r"(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
        text
    )
    for match in phone_matches:
        phones.add(match.group(0))

    # Из tel: ссылок
    for link in soup.find_all("a", href=re.compile(r"^tel:")):
        href = link.get("href", "").replace("tel:", "")
        phones.add(href)

    # Telegram
    tgs = set()
    tg = extract_telegram(text)
    if tg:
        tgs.add(tg)
    for link in soup.find_all("a", href=re.compile(r"t\.me/")):
        href = link.get("href", "")
        tg = extract_telegram(href)
        if tg:
            tgs.add(tg)

    # WhatsApp
    wats = set()
    wa = extract_whatsapp(text)
    if wa:
        wats.add(wa)
    for link in soup.find_all("a", href=re.compile(r"wa\.me/")):
        href = link.get("href", "")
        wats.add(href)

    return {
        "emails": list(emails),
        "phones": list(phones),
        "telegram": list(tgs),
        "whatsapp": list(wats),
    }


async def enrich_company(client: httpx.AsyncClient, company: dict) -> dict:
    """Обогащает данные компании контактами с сайта"""
    site = company.get("site", "") or company.get("hh_url", "")
    base_url = normalize_url(site)

    if not base_url:
        return company

    # Пропускаем известные job-порталы (там нет контактов компании)
    skip_domains = ["hh.ru", "hh.kz", "headhunter", "adata.kz", "threads.net",
                    "kaspi.kz", "linkedin.com", "instagram.com", "facebook.com"]
    if any(d in base_url.lower() for d in skip_domains):
        return company

    log.info(f"Обогащение контактов: {company.get('name', '')} ({base_url})")

    # 1. Пробуем найти страницу контактов
    contact_url = await find_contact_page(client, base_url)

    pages_to_parse = [base_url]
    if contact_url and contact_url != base_url:
        pages_to_parse.append(contact_url)

    all_emails = set()
    all_phones = set()
    all_telegram = set()
    all_whatsapp = set()

    for page_url in pages_to_parse:
        html = await fetch_page(client, page_url, timeout=12.0)
        if html:
            contacts = await parse_contacts_from_page(html)
            all_emails.update(contacts["emails"])
            all_phones.update(contacts["phones"])
            all_telegram.update(contacts["telegram"])
            all_whatsapp.update(contacts["whatsapp"])
        await asyncio.sleep(0.5)

    # Обновляем компанию
    enriched = dict(company)

    # Email: берём первый найденный, если раньше не было
    if all_emails and not enriched.get("email"):
        # Предпочитаем info@, sales@, contact@, hello@, а не noreply
        preferred = [e for e in all_emails if any(p in e.lower() for p in ["info", "sales", "contact", "hello", "manager", "director"])]
        enriched["email"] = preferred[0] if preferred else list(all_emails)[0]

    # Телефон: берём первый найденный, если раньше не было
    if all_phones and not enriched.get("phone"):
        enriched["phone"] = list(all_phones)[0]

    # Дополнительные контакты
    if all_telegram:
        enriched["telegram"] = list(all_telegram)[0]
    if all_whatsapp:
        enriched["whatsapp"] = list(all_whatsapp)[0]

    # Сохраняем все найденные контакты для справки
    enriched["_enriched_contacts"] = {
        "emails": list(all_emails),
        "phones": list(all_phones),
        "telegram": list(all_telegram),
        "whatsapp": list(all_whatsapp),
        "parsed_pages": pages_to_parse,
    }

    log.info(f"  Найдено: {len(all_emails)} email, {len(all_phones)} телефонов")
    return enriched


async def enrich_companies(companies: List[dict], max_concurrent: int = 5) -> List[dict]:
    """Обогащает список компаний с ограничением параллелизма"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _enrich(c):
        async with semaphore:
            async with httpx.AsyncClient(timeout=15.0) as client:
                return await enrich_company(client, c)

    tasks = [_enrich(c) for c in companies]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = []
    for c, res in zip(companies, results):
        if isinstance(res, Exception):
            log.warning(f"Ошибка обогащения {c.get('name')}: {res}")
            enriched.append(c)
        else:
            enriched.append(res)

    return enriched


async def main():
    parser = argparse.ArgumentParser(description="Contact Enricher")
    parser.add_argument("--input", required=True, help="Входной JSON с лидами")
    parser.add_argument("--output", required=True, help="Выходной JSON с обогащёнными лидами")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Макс. параллельных запросов")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    companies = data.get("leads", data.get("companies", []))
    log.info(f"Загружено {len(companies)} компаний для обогащения")

    enriched = await enrich_companies(companies, max_concurrent=args.max_concurrent)

    # Обновляем данные
    if "leads" in data:
        data["leads"] = enriched
    else:
        data["companies"] = enriched

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Статистика
    with_email = sum(1 for c in enriched if c.get("email"))
    with_phone = sum(1 for c in enriched if c.get("phone"))
    newly_enriched = sum(1 for c in enriched if c.get("_enriched_contacts"))

    log.info(f"Обогащение завершено:")
    log.info(f"  Всего компаний: {len(enriched)}")
    log.info(f"  С email: {with_email}")
    log.info(f"  С телефоном: {with_phone}")
    log.info(f"  Обогащено с сайтов: {newly_enriched}")
    log.info(f"  Результат: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())