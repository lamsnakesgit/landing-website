import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://hh.ru/employer/10214909"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Запишем HTML для анализа
            with open("scratch/employer_detail.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
                
            # Ищем ссылку на сайт
            # В hh.ru обычно это ссылка с data-qa="sidebar-employer-site" или href к внешнему сайту
            site_el = soup.find(attrs={"data-qa": "sidebar-employer-site"})
            if site_el:
                print(f"Site found: {site_el.get('href')} ({site_el.get_text(strip=True)})")
            else:
                # Попробуем найти другие ссылки
                print("Site not found with data-qa='sidebar-employer-site'")
                links = soup.find_all("a", href=True)
                for l in links:
                    href = l.get("href")
                    if "employer-site" in href or "target" in l.attrs:
                        print(f"Possible site link: {href} ({l.get_text(strip=True)})")
            
            # Ищем описание
            desc_el = soup.find(attrs={"data-qa": "employer-description"})
            if desc_el:
                print(f"Description: {desc_el.get_text(strip=True)[:200]}...")
            else:
                desc_el = soup.select_one(".g-user-content")
                if desc_el:
                    print(f"Description (g-user-content): {desc_el.get_text(strip=True)[:200]}...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
