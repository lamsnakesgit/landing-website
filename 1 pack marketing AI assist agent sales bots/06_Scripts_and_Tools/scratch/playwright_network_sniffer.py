import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Перехватываем запросы
        def handle_request(request):
            if "api" in request.url or "search" in request.url or "vacancy" in request.url:
                print(f"Request: {request.method} {request.url}")
                if request.post_data:
                    print(f"  Post Data: {request.post_data}")
        
        def handle_response(response):
            if "api" in response.url or "search" in response.url or "vacancy" in response.url:
                print(f"Response: {response.status} {response.url}")
                try:
                    if "json" in response.headers.get("content-type", ""):
                        print(f"  JSON Length: {len(response.text())}")
                except Exception:
                    pass

        page.on("request", handle_request)
        page.on("response", handle_response)
        
        print("Открываем страницу...")
        page.goto("https://work.adata.kz/vacancy", timeout=60000)
        time.sleep(3)
        
        # Находим поле поиска
        search_input = page.locator('input[aria-label="Для поиска вакансии введите профессию, должность или наименование компании"]').first
        search_input.fill("ии")
        time.sleep(1)
        
        print("Кликаем кнопку поиска...")
        # Ищем кнопку поиска (обычно "Найти" или с иконкой)
        search_button = page.locator('button:has-text("Найти")').first
        search_button.click()
        
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    run()
