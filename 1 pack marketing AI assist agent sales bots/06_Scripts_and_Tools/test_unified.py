import asyncio
from playwright.async_api import async_playwright
import os

async def run_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--ignore-certificate-errors',
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=BlockInsecurePrivateNetworkRequests,IsolateOrigins,site-per-process'
            ]
        )
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        
        page = await context.new_page()
        page.on("console", lambda msg: print("CONSOLE:", msg.text))
        
        print("Navigating to eGov...")
        await page.goto('https://idp.egov.kz/idp/oauth/authorize?response_type=code&client_id=office_sud&redirect_uri=https://office.sud.kz/new/redirect.xhtml&state=office_sud&scope=user:basic:read&lang=ru', timeout=60000)
        await page.wait_for_load_state('load')
        await page.wait_for_timeout(3000)
        
        print("Clicking EDS tab...")
        await page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('button, a, div.tab'));
            const edsLink = links.find(el => el.textContent && el.textContent.includes('ЭЦП'));
            if(edsLink) edsLink.click();
        }""")
        
        await page.wait_for_timeout(2000)
        
        print("Clicking Выбрать сертификат...")
        await page.evaluate("""() => {
            const btn = document.getElementById('buttonSelectCert');
            if(btn) btn.click();
        }""")
        
        print("Waiting for auth result (15s)...")
        await page.wait_for_timeout(15000)
        print("Current URL:", page.url)
        await page.screenshot(path='/opt/ai_lawyer/scripts/egov_final_auth.png')
        print("Browser test finished.")

if __name__ == '__main__':
    asyncio.run(run_browser())
