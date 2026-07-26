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
        
        # Переходим на профиль Threads напрямую
        url = "https://www.threads.net/@denc0der"
        print("Navigating to:", url)
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        # Скриншот
        await page.screenshot(path="scratch/threads_profile.png")
        print("Screenshot saved to scratch/threads_profile.png")
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем био и описание
        bio_el = soup.select_one('meta[property="og:description"]')
        if bio_el:
            print("Bio from meta:", bio_el.get('content'))
        else:
            print("Meta description not found")
            
        await browser.close()

asyncio.run(run())
