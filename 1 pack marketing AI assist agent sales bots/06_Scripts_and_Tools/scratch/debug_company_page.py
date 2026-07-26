import time
from playwright.sync_api import sync_playwright

def inspect_company():
    print("Inspecting company page on pk.adata.kz...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            # Let's open one of the companies
            url = "https://pk.adata.kz/company/220140013357"
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            # Print page title
            print("Title:", page.title())
            
            # Dump page text to find where contacts are
            body_text = page.inner_text("body")
            
            # Print sections that contain email or phone
            # We can search for phone numbers and print their surrounding text
            import re
            
            # Find all text paragraphs or divs that contain "@"
            elements = page.query_selector_all("div")
            print(f"Total divs: {len(elements)}")
            
            for el in elements:
                try:
                    text = el.inner_text().strip()
                    if "@" in text and len(text) < 200:
                        # Print selector and text
                        print(f"Div with '@': class='{el.get_attribute('class')}', text='{text}'")
                except:
                    pass
                    
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_company()
