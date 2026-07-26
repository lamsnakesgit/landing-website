import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote

def clean_yahoo_url(url):
    if "r.search.yahoo.com" in url:
        match = re.search(r'/RU=([^/]+)', url)
        if match:
            return unquote(match.group(1))
    return url

async def test_yahoo_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        queries = ["ии", "разработка ботов", "маркетинг ии", "контекстная реклама"]
        
        for query in queries:
            q = f"site:threads.net {query}"
            url = f"https://search.yahoo.com/search?q={q}"
            print(f"\n--- Query: {query} ---")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(3000)
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Ищем все результаты
                links = []
                for a in soup.find_all('a'):
                    href = a.get('href', '')
                    if 'threads.net' in href:
                        cleaned = clean_yahoo_url(href)
                        title = a.get_text().strip()
                        # Нам нужны только ссылки на профили (содержащие @) или посты /t/
                        if '@' in cleaned or '/t/' in cleaned:
                            links.append((title, cleaned))
                
                # Убираем дубликаты по URL
                unique_links = []
                seen_urls = set()
                for title, href in links:
                    if href not in seen_urls:
                        seen_urls.add(href)
                        unique_links.append((title, href))
                        
                print(f"Found {len(unique_links)} unique Threads links:")
                for title, href in unique_links[:10]:
                    print(f" - Title: {title}\n   URL: {href}")
                    
            except Exception as e:
                print(f"Query {query} failed: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_yahoo_all())
