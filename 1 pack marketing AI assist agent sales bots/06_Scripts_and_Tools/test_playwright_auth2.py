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
        resp = await page.goto("https://office.sud.kz/index.xhtml", wait_until="networkidle")
        
        await page.screenshot(path="playwright_sud_test.png")
        print("Screenshot saved to playwright_sud_test.png")
        await browser.close()

asyncio.run(main())
