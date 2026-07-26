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

async def test_yahoo_profiles():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = 'site:threads.net "@" разработка'
        url = f"https://search.yahoo.com/search?q={q}"
        print(f"Navigating to Yahoo: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # В Yahoo каждый результат поиска обычно лежит в li
            results = soup.select('ol.reg li') or soup.select('div.algo-sr')
            print(f"Found {len(results)} raw search result blocks")
            
            leads = []
            for item in results:
                title_link = item.find('a')
                if not title_link:
                    continue
                href = title_link.get('href', '')
                cleaned_url = clean_yahoo_url(href)
                print(f"Raw href: {href[:50]}... Cleaned: {cleaned_url}")
                
                # Ищем сниппет
                snippet_div = item.find('div', class_='compText') or item.find('span', class_='fc-falcon') or item.find('div', class_='desc')
                snippet = snippet_div.get_text().strip() if snippet_div else ""
                
                title = title_link.get_text().strip()
                
            # Ищем профили или посты
                if 'threads.net' in cleaned_url:
                    print(f"\nMatch found! URL: {cleaned_url}")
                    print(f"Title: {title}")
                    print(f"Snippet: {snippet}")
                    
                    # Пробуем извлечь юзернейм из заголовка или сниппета
                    # В Threads сниппет может быть вида "@username: текст поста..." или содержать юзернеймы
                    usernames = re.findall(r'@([a-zA-Z0-9_\.]+)', title + " " + snippet)
                    if usernames:
                        username = usernames[0]
                        leads.append({
                            "username": username,
                            "url": f"https://www.threads.net/@{username}",
                            "title": title,
                            "snippet": snippet
                        })
            
            print(f"\nExtracted {len(leads)} Threads profiles:")
            for l in leads:
                print(f"Username: @{l['username']}")
                print(f"URL: {l['url']}")
                print(f"Title: {l['title']}")
                print(f"Snippet: {l['snippet']}\n")
                
        except Exception as e:
            print(f"Yahoo Search failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_yahoo_profiles())
