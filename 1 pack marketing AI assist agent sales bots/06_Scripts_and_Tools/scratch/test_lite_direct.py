import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def test_lite_direct():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка"
        url = f"https://lite.duckduckgo.com/lite/?q={q}"
        print(f"Navigating to DDG Lite: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # В DDG Lite результаты лежат в таблице. Каждый результат - это tr
            # Давайте найдем все ссылки
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if 'threads.net' in href:
                    links.append((a.get_text().strip(), href))
            
            print(f"Found {len(links)} links with threads.net:")
            for text, href in links[:10]:
                print(f" - {text} -> {href}")
                
            # Давайте также посмотрим на все tr с классом или без
            print("Total tr elements:", len(soup.find_all('tr')))
            
        except Exception as e:
            print(f"DDG Lite failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_lite_direct())
