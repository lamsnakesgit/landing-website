import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        
        with open('/tmp/sud_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        try:
            await page.goto("https://office.sud.kz/index.xhtml", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            print("Goto error:", e)
        
        html = await page.content()
        if 'logout' in html or 'Шығу' in html or 'Выйти' in html:
            print("SUCCESS! LOGGED IN!")
        else:
            print("FAILED! STILL GUEST.")
            
        await browser.close()

asyncio.run(main())
