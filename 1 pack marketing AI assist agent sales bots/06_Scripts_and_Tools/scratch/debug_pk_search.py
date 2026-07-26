import time
from playwright.sync_api import sync_playwright

def debug_search():
    print("Debugging search element on pk.adata.kz...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-disable-blink-features", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) }")
        
        try:
            page.goto("https://pk.adata.kz/", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            # Print page title
            print("Title:", page.title())
            
            # Find the input elements by looking at the page HTML
            html = page.content()
            
            # Let's find all input elements and print their details
            inputs = page.query_selector_all("input")
            print(f"Total inputs: {len(inputs)}")
            for i, inp in enumerate(inputs):
                placeholder = inp.get_attribute("placeholder") or ""
                id_attr = inp.get_attribute("id") or ""
                name_attr = inp.get_attribute("name") or ""
                class_attr = inp.get_attribute("class") or ""
                type_attr = inp.get_attribute("type") or ""
                print(f"Input {i}: id='{id_attr}', name='{name_attr}', type='{type_attr}', placeholder='{placeholder}', class='{class_attr}'")
            
            # Find all buttons containing text "Найти"
            buttons = page.query_selector_all("button")
            print(f"Total buttons: {len(buttons)}")
            for i, btn in enumerate(buttons):
                text = btn.inner_text().strip()
                id_attr = btn.get_attribute("id") or ""
                class_attr = btn.get_attribute("class") or ""
                print(f"Button {i}: text='{text}', id='{id_attr}', class='{class_attr}'")
                
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    debug_search()
