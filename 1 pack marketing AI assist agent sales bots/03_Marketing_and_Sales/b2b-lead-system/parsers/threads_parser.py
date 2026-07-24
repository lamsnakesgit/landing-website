"""
threads.net Parser — профили, эксперты и компании с Threads
"""

import os
import re
import asyncio
import logging
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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

async def parse_threads_async(query: str, max_results: int = 15) -> Dict:
    log.info(f"Threads.net — запуск Playwright скрапинга по запросу: '{query}'")
    companies = []
    seen_usernames = set()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            url = f"https://www.threads.net/search?q={query}"
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Немного прокрутим вниз для загрузки карточек
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(2000)
            
            links = await page.query_selector_all('a[href*="/@"]')
            
            for l in links:
                href = await l.get_attribute("href")
                if not href or "/post/" in href:
                    continue
                    
                match = re.search(r"/@([a-zA-Z0-9_\.]+)", href)
                if not match:
                    continue
                    
                username = match.group(1)
                if username in seen_usernames:
                    continue
                seen_usernames.add(username)
                
                raw_text = await l.inner_text()
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                disp_name = lines[0] if lines else username
                
                profile_url = f"https://www.threads.net/@{username}"
                
                email = extract_email(raw_text)
                phone = extract_phone(raw_text)
                
                companies.append({
                    "id": f"threads_{username}",
                    "name": f"{disp_name} (@{username})",
                    "site": profile_url,
                    "phone": phone,
                    "email": email,
                    "city": "Удалённо / СНГ",
                    "description": f"Профиль Threads по теме: {query}. Аккаунт: @{username}",
                    "category": f"Threads: {query}",
                    "source": "threads.net",
                    "hh_url": profile_url,
                })
                
                if len(companies) >= max_results:
                    break
                    
            await browser.close()
    except Exception as e:
        log.error(f"Ошибка при скрапинге Threads.net через Playwright: {e}")

    log.info(f"Threads.net поиск завершен. Найдено профилей: {len(companies)}")
    return {
        "companies": companies,
        "vacancies": [],
        "contacts": []
    }

def parse_threads(query: str, max_results: int = 15) -> Dict:
    return asyncio.run(parse_threads_async(query, max_results))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = parse_threads("маркетинг")
    print(res)
