import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors', '--no-sandbox'])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        page.on("request", lambda request: print(f"> Request: {request.method} {request.url}"))
        page.on("websocket", lambda ws: print(f"> WebSocket opened: {ws.url}"))
        
        print("Navigating to office.sud.kz...")
        try:
            await page.goto('https://office.sud.kz/', timeout=60000)
            await page.wait_for_load_state('networkidle')
            print("Page loaded. Taking screenshot...")
            await page.screenshot(path='/opt/ai_lawyer/scripts/sud_home.png')
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
