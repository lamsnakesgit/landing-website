import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_request(request):
            if "work-api" in request.url:
                print(f"API Request: {request.method} {request.url}")
        
        def handle_response(response):
            if "work-api" in response.url:
                print(f"API Response: {response.status} {response.url}")
                try:
                    print(f"  Response Body: {response.text()[:200]}")
                except Exception:
                    pass

        page.on("request", handle_request)
        page.on("response", handle_response)
        
        print("Открываем страницу вакансии...")
        page.goto("https://work.adata.kz/vacancy/95553", timeout=60000)
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    run()
