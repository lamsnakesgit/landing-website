import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use Russian language in browser locale to get Russian UI
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
            timezone_id="Europe/Moscow"
        )
        page = await context.new_page()
        
        q = "site:threads.net разработка ботов"
        search_url = f"https://www.google.com/search?q={q}"
        print(f"Navigating to {search_url}...")
        await page.goto(search_url)
        await page.wait_for_timeout(2000)
        
        # Check if consent page is shown
        title = await page.title()
        print(f"Page title: {title}")
        
        if "Before you continue" in title or "consent" in page.url or "Согласие" in title or "Google" == title:
            print("Consent page detected! Trying to bypass...")
            # Google accept buttons
            buttons = [
                "button#L2AGLb",  # Accept all
                "button:has-text('Принять всё')",
                "button:has-text('Accept all')",
                "button:has-text('Я согласен')",
                "button:has-text('Согласен')"
            ]
            for selector in buttons:
                try:
                    if await page.locator(selector).count() > 0:
                        print(f"Clicking {selector}...")
                        await page.click(selector, timeout=2000)
                        await page.wait_for_timeout(2000)
                        print(f"New page title: {await page.title()}")
                        break
                except Exception as e:
                    print(f"Failed to click {selector}: {e}")
                    
        # Check results
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.select('div.g')
        print(f"Found {len(results)} results")
        for i, r in enumerate(results[:3]):
            title_el = r.select_one('h3')
            link_el = r.select_one('a')
            if title_el and link_el:
                print(f"[{i+1}] {title_el.get_text()} -> {link_el.get('href')}")
                
        await browser.close()

asyncio.run(run())
