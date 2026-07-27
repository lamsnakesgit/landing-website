"""
adata.kz Parser — компании, БИН, ЛПР и контакты из pk.adata.kz
"""

import httpx
import asyncio
import argparse
import json
import re
import logging
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def extract_email(text: str) -> Optional[str]:
    if not text:
        return ""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> Optional[str]:
    if not text:
        return ""
    match = re.search(r"[\+7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    return match.group(0) if match else ""

async def search_adata_async(city: str, sphere: str, role: str = "", max_pages: int = 1) -> Dict:
    query = f"{sphere} {role}".strip()
    log.info(f"adata.kz (pk.adata.kz) — запуск сбора компаний по запросу: '{query}' ({city})")

    companies = {}
    vacancies = []
    contacts = []

    url = f"https://pk.adata.kz/search?query={query}"
    content = ""

    # 1. Пробуем быстрый прямой запрос через httpx
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                content = resp.text
    except Exception as e:
        log.warning(f"httpx запрос к adata.kz не удался ({e}), пробуем Playwright...")

    # 2. Если httpx не вернул контент, пробуем Playwright
    if not content:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2000)
                content = await page.content()
                await browser.close()
        except Exception as pe:
            log.error(f"Playwright скрапинг adata.kz не удался: {pe}")

    if content:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=lambda h: h and '/company/' in h)
            
            for l in links:
                comp_url = l.get('href', '').split('?')[0]
                if not comp_url.startswith('http'):
                    comp_url = f"https://pk.adata.kz{comp_url}"
                    
                bin_match = re.search(r"/company/(\d+)", comp_url)
                bin_code = bin_match.group(1) if bin_match else ""
                
                card = l.find_parent('div', class_=re.compile(r'card|item|company')) or l.parent.parent
                card_text = card.get_text("\n", strip=True) if card else ""
                
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                comp_name = lines[0] if lines else f"Компания БИН {bin_code}"
                
                director = ""
                address = city
                
                for i, line in enumerate(lines):
                    if "Руководитель" in line and i + 1 < len(lines):
                        director = lines[i + 1]
                    if "Адрес" in line and i + 1 < len(lines):
                        address = lines[i + 1]
                        
                comp_id = f"adata_{bin_code}" if bin_code else comp_name
                
                if comp_id not in companies:
                    phone = extract_phone(card_text)
                    email = extract_email(card_text)
                    
                    companies[comp_id] = {
                        "id": comp_id,
                        "name": comp_name,
                        "bin": bin_code,
                        "inn": bin_code,
                        "site": comp_url,
                        "phone": phone,
                        "email": email,
                        "city": address or city,
                        "description": f"ЛПР: {director or 'Руководство компании'}. БИН: {bin_code}. Адрес: {address}",
                        "category": sphere,
                        "source": "adata.kz",
                        "hh_url": comp_url,
                        "director": director
                    }
                    
                    if director or phone or email:
                        contacts.append({
                            "company_id": comp_id,
                            "vacancy_id": "",
                            "name": director or "Руководитель ЛПР",
                            "role": "Директор / Руководитель (ЛПР)",
                            "email": email,
                            "phone": phone,
                            "contact_link": comp_url,
                            "source": "adata.kz"
                        })
        except Exception as e:
            log.error(f"Ошибка разбора HTML adata.kz: {e}")

    log.info(f"adata.kz сбор завершен. Компаний: {len(companies)}")
    return {
        "companies": list(companies.values()),
        "vacancies": vacancies,
        "contacts": contacts,
    }

def search_adata(city: str, sphere: str, role: str = "", max_pages: int = 1) -> dict:
    return asyncio.run(search_adata_async(city, sphere, role, max_pages))

if __name__ == "__main__":
    res = search_adata("Алматы", "маркетинг")
    print(f"Найдено компаний: {len(res['companies'])}")
