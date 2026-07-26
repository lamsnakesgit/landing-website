import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Установим большой размер окна, чтобы все элементы помещались
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        print("[*] Открываем pk.uchet.kz...")
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        
        # 1. Закрываем баннер кук, если он есть
        cookie_btn = page.locator("button:has-text('Принимаю')").first
        if cookie_btn.count() > 0 and cookie_btn.is_visible():
            print("[+] Найден баннер кук. Кликаем 'Принимаю'...")
            cookie_btn.click()
            time.sleep(2)
        else:
            print("[-] Баннер кук не найден или не виден.")
            
        # 2. Кликаем по кнопке поиска
        search_btn = page.locator("button:has-text('Введите')").first
        if search_btn.count() > 0:
            print(f"[+] Найдена кнопка поиска. Видима: {search_btn.is_visible()}. Кликаем...")
            try:
                search_btn.click(force=True) # Используем force=True на случай перекрытия
                print("[+] Кликнули по кнопке поиска.")
                time.sleep(2)
            except Exception as e:
                print("[-] Ошибка при клике на кнопку поиска:", e)
                
            # Проверяем инпуты
            inputs = page.query_selector_all("input")
            print(f"Инпуты после клика: {len(inputs)}")
            for idx, inp in enumerate(inputs):
                placeholder = inp.get_attribute("placeholder") or ""
                print(f"  Input {idx}: placeholder='{placeholder}'")
                
            # Если есть инпуты, вводим поисковый запрос
            if len(inputs) > 0:
                page.fill("input", "Казахтелеком")
                time.sleep(1)
                page.keyboard.press("Enter")
                print("[*] Отправили запрос 'Казахтелеком', ждем результатов...")
                time.sleep(5)
                
                print("URL после поиска:", page.url)
                
                # Ищем ссылки результатов
                links = page.query_selector_all("a")
                print(f"Всего ссылок после поиска: {len(links)}")
                for idx, l in enumerate(links):
                    href = l.get_attribute("href") or ""
                    text = l.inner_text().strip().replace("\n", " ")
                    if href.startswith("/c/") or "/c/" in href:
                        print(f"Результат: '{text}' -> {href}")
        else:
            print("[-] Кнопка поиска не найдена.")
            
        browser.close()

if __name__ == "__main__":
    main()
