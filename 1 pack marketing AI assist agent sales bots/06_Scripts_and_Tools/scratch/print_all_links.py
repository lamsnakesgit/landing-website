import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://pk.uchet.kz/search?query=Казахтелеком", wait_until="networkidle")
        time.sleep(5)
        
        print("Page URL:", page.url)
        links = page.query_selector_all("a")
        print(f"Total links: {len(links)}")
        for idx, l in enumerate(links):
            href = l.get_attribute("href") or ""
            text = l.inner_text().strip().replace("\n", " ")
            print(f"Link {idx}: '{text}' -> {href}")
            
        # Запишем также все кнопки
        buttons = page.query_selector_all("button")
        print(f"Total buttons: {len(buttons)}")
        for idx, b in enumerate(buttons):
            text = b.inner_text().strip().replace("\n", " ")
            print(f"Button {idx}: '{text}'")
            
        # Посмотрим текст страницы
        text_content = page.inner_text("body")
        print("\n=== BODY TEXT ===")
        print(text_content[:2000])
        
        browser.close()

if __name__ == "__main__":
    main()
