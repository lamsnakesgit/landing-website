import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print("Navigating to work.adata.kz")
        await page.goto("https://work.adata.kz")
        await page.wait_for_timeout(5000)
        
        # Скриншот главной
        await page.screenshot(path="scratch/adata_work_home.png")
        print("Screenshot saved to scratch/adata_work_home.png")
        
        # HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем формы поиска, инпуты и ссылки
        print("Page title:", await page.title())
        print("Inputs:")
        for inp in soup.find_all('input'):
            print(inp.get('name'), inp.get('placeholder'), inp.get('class'))
            
        print("Links:")
        for a in soup.find_all('a')[:20]:
            print(a.get_text(strip=True), "->", a.get('href'))
            
        await browser.close()

asyncio.run(run())
