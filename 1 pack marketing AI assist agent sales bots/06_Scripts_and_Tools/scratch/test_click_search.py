import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("[*] Открываем pk.uchet.kz...")
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        
        # Ищем кнопку для поиска
        search_btn = page.locator("button:has-text('Введите')").first
        if search_btn.count() > 0:
            print("[+] Найдена кнопка поиска. Кликаем по ней...")
            search_btn.click()
            time.sleep(2)
            
            # Смотрим, какие инпуты появились
            inputs = page.query_selector_all("input")
            print(f"Total inputs after click: {len(inputs)}")
            for idx, inp in enumerate(inputs):
                placeholder = inp.get_attribute("placeholder") or ""
                inp_type = inp.get_attribute("type") or ""
                inp_id = inp.get_attribute("id") or ""
                print(f"Input {idx}: placeholder='{placeholder}', type='{inp_type}', id='{inp_id}'")
                
            # Если есть инпут, попробуем ввести текст
            if len(inputs) > 0:
                print("[*] Вводим 'Казахтелеком' в первый инпут...")
                page.fill("input", "Казахтелеком")
                time.sleep(1)
                page.keyboard.press("Enter")
                print("[*] Нажали Enter, ждем результатов...")
                time.sleep(5)
                
                # Проверим, изменился ли URL
                print("New URL:", page.url)
                print("New Title:", page.title())
                
                # Выведем все ссылки
                links = page.query_selector_all("a")
                print(f"Total links: {len(links)}")
                for idx, l in enumerate(links):
                    href = l.get_attribute("href") or ""
                    text = l.inner_text().strip().replace("\n", " ")
                    if href.startswith("/c/") or "/c/" in href:
                        print(f"Link {idx}: '{text}' -> {href}")
        else:
            print("[-] Кнопка поиска не найдена.")
            
        browser.close()

if __name__ == "__main__":
    main()
    
