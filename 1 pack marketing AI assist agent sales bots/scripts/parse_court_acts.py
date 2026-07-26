#!/usr/bin/env python3
# Парсер судебных актов по трудовым спорам
# Использует сохранённую сессию office.sud.kz

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

COOKIES_FILE = '/opt/ai_lawyer/session_cookies.json'
OUTPUT_DIR = Path('/opt/ai_lawyer/data')
OUTPUT_DIR.mkdir(exist_ok=True)

async def parse_court_acts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={'width': 1280, 'height': 900})

        # Загружаем сессию
        with open(COOKIES_FILE) as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()

        # Открываем раздел "Мои дела" или банк актов
        print('[1] Заходим в Судебный Кабинет...')
        await page.goto('https://office.sud.kz/main',
                        wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/opt/ai_lawyer/scripts/main_auth.png')
        print(f'    URL: {page.url}')

        # Ищем раздел с делами
        print('[2] Ищем разделы с делами...')
        links = await page.query_selector_all('a[href]')
        case_links = []
        for link in links:
            href = await link.get_attribute('href') or ''
            text = (await link.inner_text()).strip()
            if any(x in href.lower() for x in ['case', 'deal', 'delo', 'act', 'claim']):
                case_links.append((text, href))
                print(f'    {text[:50]} -> {href}')

        # Пробуем раздел личных дел
        personal_urls = [
            'https://office.sud.kz/new/myCases/index.xhtml',
            'https://office.sud.kz/new/cases/index.xhtml',
            'https://office.sud.kz/new/myDocuments/index.xhtml',
            'https://office.sud.kz/new/claims/index.xhtml',
        ]

        print('[3] Проверяем разделы с делами...')
        for url in personal_urls:
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(1500)
                title = await page.title()
                body = await page.inner_text('body')
                length = len(body)
                is_auth = 'Кіру' not in body and 'Войти' not in body
                print(f'    {"OK" if is_auth else "REDIRECT"} {url}')
                print(f'    Title: {title} | Body: {length} chars')
                if is_auth and length > 1000:
                    await page.screenshot(path=f'/opt/ai_lawyer/scripts/section_{url.split("/")[-1]}.png')
                    print(f'    Сохранен скриншот!')
                    print(f'    Контент: {body[:300]}')
            except Exception as e:
                print(f'    FAIL {url}: {e}')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(parse_court_acts())
