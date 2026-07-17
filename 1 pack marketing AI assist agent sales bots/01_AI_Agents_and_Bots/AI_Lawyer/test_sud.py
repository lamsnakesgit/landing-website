import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to https://office.sud.kz/...")
        try:
            response = await page.goto("https://office.sud.kz/", timeout=60000)
            print(f"Status: {response.status}")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(5000) # Wait 5 seconds for JS to render
            html = await page.content()
            with open("sud_homepage.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved to sud_homepage.html")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
