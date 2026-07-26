import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        
        with open('/tmp/sud_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        await page.goto("https://office.sud.kz/index.xhtml", wait_until="domcontentloaded")
        
        html = await page.content()
        if 'logout' in html or 'Шығу' in html or 'Выйти' in html:
            print("SUCCESS! Playwright sees we are LOGGED IN!")
            # Print the title
            title = await page.title()
            print("Page Title:", title)
        else:
            print("FAILED. Playwright sees GUEST.")
            
        await browser.close()

asyncio.run(main())
