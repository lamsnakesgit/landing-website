import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
            timezone_id="Europe/Moscow"
        )
        page = await context.new_page()
        
        q = "site:threads.net боты"
        search_url = f"https://www.google.com/search?q={q}"
        print(f"Navigating to {search_url}...")
        await page.goto(search_url)
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print(f"Page title: {title}")
        print(f"Current URL: {page.url}")
        
        os.makedirs("scratch", exist_ok=True)
        # Сохраним HTML
        html = await page.content()
        with open("scratch/google_search.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # Сделаем скриншот
        await page.screenshot(path="scratch/google_search.png")
        print("Screenshot saved to scratch/google_search.png")
        
        await browser.close()

asyncio.run(run())
