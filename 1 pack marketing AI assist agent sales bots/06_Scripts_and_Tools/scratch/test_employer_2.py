import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://hh.ru/employer/1797187"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            print("=== EXTERNAL LINKS ===")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)
                if not href.startswith("/") and "hh.ru" not in href and "hh.kz" not in href:
                    print(f"Href: {href}, Text: {text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
