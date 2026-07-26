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
        
        # Нам нужен реальный поиск по запросу "разработка"
        # На скриншоте видно, что URL "https://work.adata.kz/vacancy" без параметров просто показывает последние вакансии.
        # Давайте попробуем ввести текст в поиск и нажать кнопку "Найти".
        url = "https://work.adata.kz/vacancy"
        print("Переходим на:", url)
        await page.goto(url)
        await page.wait_for_timeout(3000)
        
        # Вводим "разработка" в поле поиска
        # Поле поиска: input или textarea с placeholder
        # Найдем плейсхолдер: "Для поиска вакансии введите профессию, должность или наименование компании"
        search_input = page.locator("input[placeholder*='Для поиска вакансии']")
        if await search_input.count() > 0:
            print("Вводим запрос 'разработка'...")
            await search_input.fill("разработка")
            await page.wait_for_timeout(500)
            
            # Нажимаем кнопку "Найти"
            # Кнопка: button с текстом "Найти"
            find_button = page.locator("button:has-text('Найти')")
            if await find_button.count() > 0:
                print("Нажимаем кнопку 'Найти'...")
                await find_button.click()
                await page.wait_for_timeout(4000)
                await page.screenshot(path="scratch/adata_work_search_results.png")
                print("Результаты поиска сохранены в scratch/adata_work_search_results.png")
        
        # Анализируем HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Найдем все ссылки
        links = soup.find_all('a')
        print(f"Всего ссылок на странице: {len(links)}")
        
        # Выведем первые 20 ссылок с href
        for i, l in enumerate(links[:30]):
            href = l.get('href', '')
            text = l.get_text(strip=True)
            print(f"[{i+1}] Текст: '{text}' | Href: '{href}'")
            
        await browser.close()

asyncio.run(run())
