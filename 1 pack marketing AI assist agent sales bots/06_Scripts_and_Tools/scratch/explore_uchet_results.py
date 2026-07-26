import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://pk.uchet.kz/search?query=Казахтелеком"
        print(f"[*] Loading {url}...")
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        # Получаем заголовок
        print("Title:", page.title())
        
        # Запишем HTML для анализа
        html = page.content()
        with open("scratch/uchet_search_results.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # Найдем все ссылки
        links = page.query_selector_all("a")
        print(f"Total links: {len(links)}")
        for l in links[:30]:
            href = l.get_attribute("href") or ""
            text = l.inner_text().strip()
            if href.startswith("/c/") or "/c/" in href:
                print(f"Link: '{text}' -> {href}")
                
        browser.close()

if __name__ == "__main__":
    main()
