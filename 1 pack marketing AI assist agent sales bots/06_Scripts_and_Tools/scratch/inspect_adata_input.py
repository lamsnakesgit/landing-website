import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def inspect_adata():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to pk.adata.kz...")
        try:
            await page.goto("https://pk.adata.kz/", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Найдем все инпуты на странице
            inputs = soup.find_all('input')
            print(f"Found {len(inputs)} input elements:")
            for i, inp in enumerate(inputs):
                print(f"[{i}] tag: {inp.name}, attributes: {inp.attrs}")
                
            # Найдем все кнопки
            buttons = soup.find_all('button')
            print(f"Found {len(buttons)} button elements:")
            for i, btn in enumerate(buttons):
                print(f"[{i}] text: {btn.get_text().strip()}, attributes: {btn.attrs}")
                
        except Exception as e:
            print(f"Failed to inspect adata: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_adata())
