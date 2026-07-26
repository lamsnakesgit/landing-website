import time
import os
from playwright.sync_api import sync_playwright

def test_pk_adata_search(query):
    print(f"Testing search on pk.adata.kz for query: {query}")
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
            print("Navigating to https://pk.adata.kz/...")
            page.goto("https://pk.adata.kz/", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            print("Current URL:", page.url)
            os.makedirs("scratch", exist_ok=True)
            page.screenshot(path="scratch/pk_adata_home.png")
            print("Screenshot saved to scratch/pk_adata_home.png")
            
            # Print page title
            print("Page Title:", page.title())
            
            # Find the search inputs
            inputs = page.query_selector_all("input")
            print(f"Found {len(inputs)} input fields.")
            for i, inp in enumerate(inputs):
                print(f"Input {i}: name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}, class={inp.get_attribute('class')}")
            
            # Try to search
            search_input = page.query_selector("input[placeholder*='Введите БИН, ИИН']") or page.query_selector("input[placeholder*='название']") or page.query_selector("input[type='text']") or page.query_selector("input")
            if search_input:
                print("Found search input! Entering query...")
                search_input.fill(query)
                time.sleep(1)
                search_input.press("Enter")
                print("Pressed Enter, waiting for navigation/results...")
                time.sleep(5)
                
                print("URL after search:", page.url)
                page.screenshot(path="scratch/pk_adata_after_search.png")
                
                # Check for links or results
                results = page.query_selector_all("a[href^='/c/']") or page.query_selector_all("a[href*='/company/']") or page.query_selector_all("a.search-result-link") or page.query_selector_all(".search-results a") or page.query_selector_all("a")
                print(f"Found {len(results)} links after search.")
                
                # Let's print some links that look like company links (usually start with /c/ or containing some text)
                valid_results = 0
                for i, r in enumerate(results):
                    href = r.get_attribute("href")
                    text = r.inner_text().strip()
                    if href and ("/c/" in href or "/company/" in href or "search-result" in (r.get_attribute("class") or "")):
                        print(f"Company Result {valid_results+1}: {text} -> {href}")
                        valid_results += 1
                        if valid_results >= 10:
                            break
            else:
                print("No search input found.")
                
        except Exception as e:
            print("Error occurred:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_pk_adata_search("ии")
