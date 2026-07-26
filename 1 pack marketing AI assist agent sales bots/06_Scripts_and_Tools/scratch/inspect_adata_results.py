import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def inspect_results():
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
            
            # Вводим запрос 'ии'
            input_sel = '[data-test-id="pk-main-page-company-search-input"]'
            button_sel = '[data-test-id="pk-main-page-company-find-button"]'
            
            await page.fill(input_sel, "ии")
            await page.click(button_sel)
            
            print("Waiting for results...")
            await page.wait_for_timeout(5000)
            
            # Сохраняем скриншот
            await page.screenshot(path="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/adata_results.png")
            print("Screenshot saved to scratch/adata_results.png")
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Найдем все ссылки
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if '/company/' in href:
                    links.append((a.get_text().strip(), href, a.attrs))
                    
            print(f"Found {len(links)} company links:")
            for i, (text, href, attrs) in enumerate(links[:10]):
                print(f"[{i}] Text: {text}\n    Href: {href}\n    Attrs: {attrs}")
                
        except Exception as e:
            print(f"Failed to inspect results: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_results())
