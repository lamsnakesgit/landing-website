import time
from playwright.sync_api import sync_playwright

def test_company(company):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = f"https://pk.uchet.kz/search/nab/?query={company}"
        print(f"[*] Переходим на {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        # Запишем HTML результатов для анализа
        html = page.content()
        with open(f"scratch/uchet_search_{company}.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        links = page.query_selector_all("a")
        print(f"Total links found: {len(links)}")
        found = False
        for l in links:
            href = l.get_attribute("href") or ""
            text = l.inner_text().strip()
            if href.startswith("/c/") or "/c/" in href:
                print(f"Match: '{text}' -> {href}")
                found = True
        if not found:
            print("[-] Ни одной ссылки /c/ не найдено")
            
        browser.close()

if __name__ == "__main__":
    test_company("Казахтелеком")
    print("-" * 50)
    test_company("Стройшахтопроект")
