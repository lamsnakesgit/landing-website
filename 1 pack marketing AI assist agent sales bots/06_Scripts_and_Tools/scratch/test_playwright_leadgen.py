import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def search_google(page, query, limit=5):
    """Ищет в Google и возвращает список найденных URL и сниппетов"""
    search_url = f"https://www.google.com/search?q={query}"
    print(f"Поиск в Google: {search_url}")
    
    try:
        await page.goto(search_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Скриншот для отладки
        safe_query = re.sub(r'[^a-zA-Z0-9]', '_', query)
        await page.screenshot(path=f"scratch/debug_{safe_query[:20]}.png")
        
        # Обход страницы согласия Google (если появится)
        title = await page.title()
        print(f"Title for {query}: {title}")
        if "Before you continue" in title or "consent" in page.url or "Согласие" in title or "Google" == title:
            print("Обнаружена страница согласия Google. Обходим...")
            buttons = [
                "button#L2AGLb",  # Принять всё
                "button:has-text('Принять всё')",
                "button:has-text('Accept all')",
                "button:has-text('Я согласен')",
                "button:has-text('Согласен')"
            ]
            for selector in buttons:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.click(selector, timeout=2000)
                        await page.wait_for_timeout(2000)
                        await page.screenshot(path=f"scratch/debug_{safe_query[:20]}_after_consent.png")
                        break
                except Exception:
                    pass
                    
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        # Google search results are typically in div.g or div.MjjYud
        for r in soup.select('div.g')[:limit]:
            title_el = r.select_one('h3')
            link_el = r.select_one('a')
            snippet_el = r.select_one('div[style*="webkit-line-clamp"], .VwiC3b')
            
            if link_el:
                url = link_el.get('href')
                title_text = title_el.get_text() if title_el else ""
                snippet_text = snippet_el.get_text() if snippet_el else ""
                results.append({
                    "url": url,
                    "title": title_text,
                    "snippet": snippet_text
                })
        return results
    except Exception as e:
        print(f"Ошибка поиска Google по запросу '{query}': {e}")
        return []

async def test_leadgen():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
            timezone_id="Asia/Almaty"
        )
        page = await context.new_page()
        
        # 1. Тестируем Threads
        print("\n=== ТЕСТ THREADS ===")
        threads_results = await search_google(page, "site:threads.net разработка ботов", limit=3)
        print(f"Найдено Threads: {len(threads_results)}")
        for r in threads_results:
            print(f"- {r['title']} ({r['url']})")
            print(f"  Сниппет: {r['snippet']}")
            
        # 2. Тестируем Adata.kz
        print("\n=== ТЕСТ ADATA.KZ ===")
        adata_results = await search_google(page, "site:pk.adata.kz/company/ разработка программного обеспечения Алматы", limit=3)
        print(f"Найдено Adata: {len(adata_results)}")
        for r in adata_results:
            print(f"- {r['title']} ({r['url']})")
            print(f"  Сниппет: {r['snippet']}")
            
        # 3. Тестируем HH.ru / HH.kz
        print("\n=== ТЕСТ HH ===")
        hh_results = await search_google(page, "site:hh.ru/vacancy/ разработка ботов", limit=3)
        print(f"Найдено HH: {len(hh_results)}")
        for r in hh_results:
            print(f"- {r['title']} ({r['url']})")
            print(f"  Сниппет: {r['snippet']}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_leadgen())
