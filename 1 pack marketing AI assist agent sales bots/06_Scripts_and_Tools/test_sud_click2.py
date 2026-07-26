import asyncio
from playwright.async_api import async_playwright
import traceback
import sys

async def run():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors', '--no-sandbox'])
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            page.on("request", lambda request: print(f"> Req: {request.method} {request.url}") if '127.0.0.1' in request.url or 'sud.kz' not in request.url else None)
            
            print("Navigating...")
            await page.goto('https://office.sud.kz/', timeout=60000)
            await page.wait_for_load_state('load')
            await page.wait_for_timeout(3000)
            
            print("Clicking login...")
            # Use JS to click the login button to avoid strict mode errors
            await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a'));
                const loginLink = links.find(a => a.textContent.includes('Или войти через') || a.textContent.includes('арқылы кіріңіз'));
                if(loginLink) loginLink.click();
            }""")
            
            await page.wait_for_timeout(4000)
            print("Taking modal screenshot...")
            await page.screenshot(path='/opt/ai_lawyer/scripts/modal.png')
            
            print("Clicking EDS...")
            # Click EDS
            await page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a, button, div, span'));
                const edsLink = links.find(a => a.textContent.includes('ЭЦП') || a.textContent.includes('ЭЦҚ'));
                if(edsLink) edsLink.click();
            }""")
            
            # Wait a bit to catch the 127.0.0.1 request
            await page.wait_for_timeout(5000)
            await page.screenshot(path='/opt/ai_lawyer/scripts/modal_after_eds.png')
            
            print("Done")
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(run())
