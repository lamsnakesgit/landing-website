import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto("https://adata.kz/", wait_until="networkidle")
        time.sleep(3)
        
        # Запишем HTML для анализа
        html_content = page.content()
        with open("scratch/adata_home_dump.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("Page title:", page.title())
        
        # Попробуем найти инпуты и кнопки
        inputs = page.query_selector_all("input")
        print(f"Total inputs: {len(inputs)}")
        for idx, i in enumerate(inputs):
            print(f"Input {idx}: id={i.get_attribute('id')}, name={i.get_attribute('name')}, placeholder='{i.get_attribute('placeholder')}', type={i.get_attribute('type')}")
            
        buttons = page.query_selector_all("button")
        print(f"Total buttons: {len(buttons)}")
        for idx, b in enumerate(buttons):
            print(f"Button {idx}: text='{b.inner_text().strip()}', id={b.get_attribute('id')}, class={b.get_attribute('class')}")
            
        browser.close()

if __name__ == "__main__":
    main()
