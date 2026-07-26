import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors', '--no-sandbox'])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        page.on("request", lambda request: print(f"> Request: {request.method} {request.url}") if '127.0.0.1' in request.url or 'localhost' in request.url else None)
        
        print("Navigating to office.sud.kz...")
        try:
            await page.goto('https://office.sud.kz/', timeout=60000)
            await page.wait_for_load_state('networkidle')
            
            # Find the "арқылы кіріңіз" (Login via) button
            login_btn = page.locator("a:has-text('арқылы кіріңіз')").first
            if await login_btn.count() > 0:
                print(f"Clicking login button...")
                await login_btn.click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path='/opt/ai_lawyer/scripts/sud_login_modal.png')
                
                # After clicking login, let's dump all text to see EDS button
                links = await page.locator("a").all_inner_texts()
                print("Links after modal:", [l for l in links if l.strip()])
                
                # Check for "ЭЦП" or "ЭЦҚ"
                eds = page.locator("a:has-text('ЭЦП'), a:has-text('ЭЦҚ')").first
                if await eds.count() > 0:
                    print("Clicking EDS...")
                    await eds.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path='/opt/ai_lawyer/scripts/sud_eds_clicked.png')
                
            else:
                print("Login button not found.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
