import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def test_yahoo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка"
        url = f"https://search.yahoo.com/search?q={q}"
        print(f"Navigating to Yahoo: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            print(f"Title: {await page.title()}")
            
            # В Yahoo результаты лежат в div.algo-sr или ol li
            results = soup.select('div.algo-sr') or soup.select('ol li')
            print(f"Yahoo found elements: {len(results)}")
            
            # Попробуем найти ссылки на threads.net
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                # Проверяем, что threads.net является частью домена в ссылке, а не параметром перенаправления
                # Ссылка на результат в Yahoo обычно идет через r.search.yahoo.com или напрямую
                if 'threads.net' in href and 'yahoo.com' not in href:
                    links.append((a.get_text().strip(), href))
                elif 'threads.net' in href and 'r.search.yahoo.com' in href:
                    # Это редирект Yahoo на результат
                    links.append((a.get_text().strip(), href))
            
            print(f"Found {len(links)} filtered threads.net links:")
            for text, href in links:
                print(f" - Text: {text}\n   URL: {href}")
                
        except Exception as e:
            print(f"Yahoo failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_yahoo())
