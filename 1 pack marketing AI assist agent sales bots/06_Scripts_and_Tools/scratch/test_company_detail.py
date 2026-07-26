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
        # Kaspi Bank
        url = "https://pk.adata.kz/company/971240001315"
        print("Navigating to company details:", url)
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        # Скриншот
        await page.screenshot(path="scratch/adata_company_detail.png")
        print("Screenshot saved to scratch/adata_company_detail.png")
        
        # HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Выведем весь текст страницы, чтобы найти контакты
        print("Page text length:", len(soup.get_text()))
        print("Some page content (first 2000 chars):")
        print(soup.get_text()[:2000])
        
        # Ищем телефон и email
        phones = soup.select(".phone, [itemprop='telephone'], a[href^='tel:']")
        emails = soup.select(".email, [itemprop='email'], a[href^='mailto:']")
        print("Phones found:", len(phones))
        for ph in phones:
            print("Phone:", ph.get_text(strip=True))
        print("Emails found:", len(emails))
        for em in emails:
            print("Email:", em.get_text(strip=True))
            
        await browser.close()

asyncio.run(run())
