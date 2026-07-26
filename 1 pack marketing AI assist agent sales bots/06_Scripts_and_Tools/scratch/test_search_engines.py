import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_bing():
    print("=== Testing Bing ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка ботов"
        search_url = f"https://www.bing.com/search?q={q}"
        print(f"Navigating to Bing: {search_url}")
        
        try:
            await page.goto(search_url, wait_until="networkidle", timeout=20000)
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # В Bing результаты лежат в li.b_algo
            results = soup.select('li.b_algo')
            print(f"Bing found {len(results)} results")
            for i, r in enumerate(results[:5]):
                link_el = r.select_one('h2 a')
                snippet_el = r.select_one('.b_caption p') or r.select_one('.b_snippet')
                
                href = link_el.get('href') if link_el else "No link"
                title = link_el.get_text() if link_el else "No title"
                snippet = snippet_el.get_text() if snippet_el else "No snippet"
                
                print(f"[{i+1}] Title: {title}\n    URL: {href}\n    Snippet: {snippet}\n")
        except Exception as e:
            print(f"Bing failed: {e}")
        finally:
            await browser.close()

async def test_google():
    print("=== Testing Google ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка ботов"
        search_url = f"https://www.google.com/search?q={q}"
        print(f"Navigating to Google: {search_url}")
        
        try:
            await page.goto(search_url, wait_until="networkidle", timeout=20000)
            
            # Проверка страницы согласия
            title = await page.title()
            print(f"Google title: {title}")
            
            if "Before you continue" in title or "consent" in page.url or "Согласие" in title or "Google" == title:
                print("Google Consent detected. Bypassing...")
                buttons = ["button#L2AGLb", "button:has-text('Принять всё')", "button:has-text('Accept all')"]
                for btn in buttons:
                    if await page.locator(btn).count() > 0:
                        await page.click(btn)
                        await page.wait_for_timeout(2000)
                        break
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Селекторы Google результатов: div.g, div[data-sokoban-container], или просто поиск ссылок с threads.net
            links = soup.find_all('a')
            threads_links = []
            for l in links:
                href = l.get('href', '')
                if 'threads.net/@' in href:
                    # Находим родителя, чтобы достать сниппет
                    parent = l.find_parent('div')
                    snippet = ""
                    if parent:
                        # Ищем текст вокруг
                        snippet = parent.get_text(strip=True)[:150]
                    threads_links.append((l.get_text(), href, snippet))
            
            print(f"Google links with threads.net: {len(threads_links)}")
            for i, (title, href, snippet) in enumerate(threads_links[:5]):
                print(f"[{i+1}] Title: {title}\n    URL: {href}\n    Snippet: {snippet}\n")
                
        except Exception as e:
            print(f"Google failed: {e}")
        finally:
            await browser.close()

async def main():
    await test_bing()
    await test_google()

if __name__ == "__main__":
    asyncio.run(main())
