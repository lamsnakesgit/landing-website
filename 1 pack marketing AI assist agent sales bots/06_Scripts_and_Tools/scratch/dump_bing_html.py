import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def dump_bing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка"
        search_url = f"https://www.bing.com/search?q={q}"
        print(f"Navigating to: {search_url}")
        
        await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)
        
        html = await page.content()
        
        # Сохраним HTML в файл для детального анализа
        dump_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/bing_dump.html"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML dumped to {dump_path}")
        
        soup = BeautifulSoup(html, 'html.parser')
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Выведем некоторые теги, чтобы понять структуру
        print("A elements: ", len(soup.find_all('a')))
        print("LI elements: ", len(soup.find_all('li')))
        
        # Попробуем найти ссылки на threads.net в тегах a
        threads_links = []
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'threads.net' in href:
                threads_links.append(href)
        print(f"Found {len(threads_links)} raw links containing 'threads.net'")
        for link in threads_links[:5]:
            print(" -", link)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_bing())
