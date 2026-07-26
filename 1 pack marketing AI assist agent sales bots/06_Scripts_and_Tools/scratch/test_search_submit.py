import time
import os
from playwright.sync_api import sync_playwright

def test_submit():
    print("Testing search submission on pk.adata.kz...")
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
            
            # Fill the input
            # The input has id = "Введите ИИН, БИН, ФИО, название компании"
            input_selector = "input[id='Введите ИИН, БИН, ФИО, название компании']"
            page.click(input_selector)
            page.fill(input_selector, "разработка")
            time.sleep(1)
            
            # Click the search button with text "Найти"
            # We can find the button that has text "Найти"
            button_selector = "button:has-text('Найти')"
            page.click(button_selector)
            
            print("Clicked search, waiting for network/navigation...")
            time.sleep(5)
            
            print("URL after click:", page.url)
            page.screenshot(path="scratch/pk_adata_search_submitted.png")
            print("Screenshot saved to scratch/pk_adata_search_submitted.png")
            
            # Check for result links
            # Let's list all links on the page that could be company links
            links = page.query_selector_all("a")
            print(f"Total links: {len(links)}")
            company_links = []
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()
                if "/c/" in href or "/company/" in href:
                    company_links.append((text, href))
            
            print(f"Found {len(company_links)} company links:")
            for i, (text, href) in enumerate(company_links[:15]):
                print(f"Company {i+1}: {text} -> {href}")
                
        except Exception as e:
            print("Error occurred:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_submit()
