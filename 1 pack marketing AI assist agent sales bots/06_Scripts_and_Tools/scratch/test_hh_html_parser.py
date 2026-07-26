import httpx
from bs4 import BeautifulSoup
import re

async def main():
    url = "https://hh.ru/search/vacancy"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    params = {
        "text": "боты",
        "area": "40", # Казахстан
        "order_by": "publication_time"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=headers, params=params, follow_redirects=True)
        print(f"Status code: {resp.status_code}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Запишем часть HTML для анализа
            with open("scratch/hh_search_result.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            
            # Попробуем найти вакансии
            # В hh.ru вакансии часто лежат в div с классом 'serp-item' или data-qa='vacancy-serp__vacancy'
            items = soup.find_all(attrs={"data-qa": "vacancy-serp__vacancy"})
            print(f"Found with data-qa='vacancy-serp__vacancy': {len(items)}")
            
            if not items:
                # Попробуем найти по селектору class
                items = soup.select(".serp-item")
                print(f"Found with class '.serp-item': {len(items)}")
                
            if not items:
                # Попробуем по ссылкам на вакансии /vacancy/
                links = soup.find_all("a", href=re.compile(r"/vacancy/\d+"))
                print(f"Found links to vacancies: {len(links)}")
                
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
