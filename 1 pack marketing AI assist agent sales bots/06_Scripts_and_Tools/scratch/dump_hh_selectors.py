import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        page = await context.new_page()
        
        url = "https://hh.ru/search/vacancy?text=разработка+ботов&area=160"
        print("Переходим на:", url)
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Найдем все ссылки <a> и выведем те, что похожи на вакансии
        links = soup.find_all('a')
        print(f"Всего ссылок на странице: {len(links)}")
        
        # Вакансии на hh обычно содержат в href "/vacancy/"
        vacancy_links = [l for l in links if '/vacancy/' in l.get('href', '')]
        print(f"Ссылок с /vacancy/: {len(vacancy_links)}")
        for i, l in enumerate(vacancy_links[:20]):
            print(f"[{i+1}] Текст: '{l.get_text(strip=True)}' | Href: '{l.get('href')}' | Classes: {l.get('class')}")
            
        await browser.close()

asyncio.run(run())
