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
        # Попробуем без /search
        url = "https://work.adata.kz/vacancy?text=разработка"
        print("Navigating to:", url)
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        # Скриншот
        await page.screenshot(path="scratch/adata_work_vacancies.png")
        print("Screenshot saved to scratch/adata_work_vacancies.png")
        
        # HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем вакансии
        links = soup.select("a[href*='/vacancy/']")
        print("Found vacancy links:", len(links))
        for i, l in enumerate(links[:15]):
            print(f"[{i+1}] {l.get_text(strip=True)} -> {l.get('href')}")
            
        await browser.close()

asyncio.run(run())
