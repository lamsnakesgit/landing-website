import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto("https://adata.kz")
        time.sleep(5)
        
        # Сделаем скриншот главной
        page.screenshot(path="scratch/adata_main.png")
        print("Главная страница загружена.")
        
        # Попробуем найти поле ввода поиска
        # Обычно это input
        inputs = page.query_selector_all("input")
        print("Найдено инпутов:", len(inputs))
        for i, inp in enumerate(inputs):
            print(f"Инпут {i}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}, id={inp.get_attribute('id')}, class={inp.get_attribute('class')}")
            
        browser.close()

if __name__ == "__main__":
    main()
