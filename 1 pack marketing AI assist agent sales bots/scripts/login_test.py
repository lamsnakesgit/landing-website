import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to office.sud.kz...")
        try:
            await page.goto('https://office.sud.kz/', timeout=60000)
            await page.wait_for_load_state('load')
            print("Page loaded. Taking screenshot...")
            await page.screenshot(path='sud_login_page.png')
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
