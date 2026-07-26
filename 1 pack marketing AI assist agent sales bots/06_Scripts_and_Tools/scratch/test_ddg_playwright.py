import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import urllib.parse
import re

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        page = await context.new_page()
        
        # Переходим на DuckDuckGo
        url = "https://html.duckduckgo.com/html/?q=site:threads.net+разработка+ботов"
        print("Navigating to:", url)
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        links = soup.select('a.result__url')
        print("Found links:", len(links))
        for i, a in enumerate(links[:15]):
            href = a.get('href', '')
            title_el = a.find_parent('div', class_='result__body')
            title = ""
            snippet = ""
            if title_el:
                t_el = title_el.select_one('.result__title')
                if t_el:
                    title = t_el.get_text(strip=True)
                s_el = title_el.select_one('.result__snippet')
                if s_el:
                    snippet = s_el.get_text(strip=True)
            
            print(f"[{i+1}] Title: {title} | Href: {href} | Snippet: {snippet}")
            
        await browser.close()

asyncio.run(run())
