import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def test_bing_parser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Попробуем запросы
        queries = ["ии", "разработка", "маркетинг"]
        for query in queries:
            q = f"site:threads.net {query}"
            search_url = f"https://www.bing.com/search?q={q}"
            print(f"\n--- Query: {query} ---")
            
            try:
                # Используем wait_until="domcontentloaded", чтобы не ждать бесконечно трекеры
                await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2000)
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = soup.select('li.b_algo')
                print(f"Bing found {len(results)} results")
                
                for i, r in enumerate(results[:5]):
                    link_el = r.select_one('h2 a')
                    if not link_el:
                        continue
                    
                    href = link_el.get('href', '')
                    title = link_el.get_text().strip()
                    
                    # Ищем сниппет
                    snippet_el = r.select_one('.b_caption p') or r.select_one('.b_snippet') or r.select_one('.line_en')
                    snippet = snippet_el.get_text().strip() if snippet_el else ""
                    
                    match = re.search(r'threads\.net/@([a-zA-Z0-9_\.]+)', href)
                    if match:
                        username = match.group(1)
                        print(f"[{i+1}] Username: @{username}")
                        print(f"    Title: {title}")
                        print(f"    URL: {href}")
                        print(f"    Snippet: {snippet}")
                    else:
                        print(f"[{i+1}] (Non-profile link) URL: {href}")
                        
            except Exception as e:
                print(f"Failed query {query}: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_bing_parser())
