import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        # We need to manually log in again just to inspect the local storage...
        # Wait, I don't want to make the user scan QR again right now if I can avoid it.
        # But if the session is gone, I have to.
        await browser.close()
asyncio.run(main())
