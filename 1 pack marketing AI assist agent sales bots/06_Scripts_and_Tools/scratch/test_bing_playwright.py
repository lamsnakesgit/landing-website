import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        page = await context.new_page()
        # Поиск в Bing
        url = "https://www.bing.com/search?q=site:threads.net+разработка+ботов"
        print("Navigating to:", url)
        await page.goto(url)
        await page.wait_for_timeout(4000)
        
        # Скриншот
        await page.screenshot(path="scratch/bing_search.png")
        print("Screenshot saved to scratch/bing_search.png")
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем результаты
        links = soup.select('li.b_algo h2 a')
        print("Found links:", len(links))
        for i, a in enumerate(links[:10]):
            print(f"[{i+1}] {a.get_text(strip=True)} -> {a.get('href')}")
            
        await browser.close()

asyncio.run(run())
