import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def test_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 1. Bing с setlang=en
        print("=== Test 1: Bing with setlang=en ===")
        url = "https://www.bing.com/search?q=site:threads.net+разработка&setlang=en"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            results = soup.select('li.b_algo')
            print(f"Title: {page.title()}")
            print(f"Results found (li.b_algo): {len(results)}")
            for i, r in enumerate(results[:3]):
                link = r.select_one('h2 a')
                print(f" - [{i}] {link.get_text() if link else 'No link'} -> {link.get('href') if link else ''}")
        except Exception as e:
            print(f"Error Test 1: {e}")
            
        # 2. Bing с setlang=ru
        print("\n=== Test 2: Bing with setlang=ru ===")
        url = "https://www.bing.com/search?q=site:threads.net+разработка&setlang=ru"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            results = soup.select('li.b_algo')
            print(f"Title: {page.title()}")
            print(f"Results found (li.b_algo): {len(results)}")
            for i, r in enumerate(results[:3]):
                link = r.select_one('h2 a')
                print(f" - [{i}] {link.get_text() if link else 'No link'} -> {link.get('href') if link else ''}")
        except Exception as e:
            print(f"Error Test 2: {e}")

        # 3. DuckDuckGo Lite
        print("\n=== Test 3: DuckDuckGo Lite ===")
        url = "https://lite.duckduckgo.com/lite/"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.fill("input[name='q']", "site:threads.net разработка")
            await page.click("input[type='submit']")
            await page.wait_for_timeout(3000)
            print(f"DDG Lite URL: {page.url}")
            print(f"DDG Lite Title: {page.title()}")
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # В DDG Lite результаты лежат в таблице
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if 'threads.net/@' in href or 'threads.net/' in href:
                    links.append((a.get_text(), href))
            print(f"Results found in DDG Lite: {len(links)}")
            for i, (text, href) in enumerate(links[:5]):
                print(f" - [{i}] {text} -> {href}")
        except Exception as e:
            print(f"Error Test 3: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search())
