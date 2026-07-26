import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def inspect_inputs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.goto("https://pk.adata.kz/", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        print("=== INPUTS ON PK.ADATA.KZ ===")
        for i, inp in enumerate(soup.find_all('input')):
            print(f"Input {i}:")
            print(f"  id: {inp.get('id')}")
            print(f"  class: {inp.get('class')}")
            print(f"  placeholder: {inp.get('placeholder')}")
            print(f"  type: {inp.get('type')}")
            print(f"  name: {inp.get('name')}")
            print(f"  attrs: {inp.attrs}")
            
        print("\n=== BUTTONS ON PK.ADATA.KZ ===")
        for i, btn in enumerate(soup.find_all('button')):
            print(f"Button {i}:")
            print(f"  text: {btn.get_text().strip()}")
            print(f"  class: {btn.get('class')}")
            print(f"  attrs: {btn.attrs}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_inputs())
