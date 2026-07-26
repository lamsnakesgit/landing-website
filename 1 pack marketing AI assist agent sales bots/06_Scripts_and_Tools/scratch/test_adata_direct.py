import time
import os
from playwright.sync_api import sync_playwright

def test_adata_search(query):
    print(f"Testing search on adata.kz starting from homepage for query: {query}")
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
            print("Navigating to https://adata.kz/...")
            page.goto("https://adata.kz/", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            print("Current URL:", page.url)
            page.screenshot(path="scratch/adata_home.png")
            print("Homepage screenshot saved.")
            
            # Find the search inputs
            inputs = page.query_selector_all("input")
            print(f"Found {len(inputs)} input fields.")
            for i, inp in enumerate(inputs):
                print(f"Input {i}: name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}, class={inp.get_attribute('class')}")
            
            # Look for a search input. Usually it has placeholder like "Введите БИН, ИИН или название"
            search_input = page.query_selector("input[placeholder*='поиск']") or page.query_selector("input[placeholder*='БИН']") or page.query_selector("input[type='text']") or page.query_selector("input")
            
            if search_input:
                print("Found search input! Typing query...")
                search_input.fill(query)
                time.sleep(1)
                search_input.press("Enter")
                print("Pressed Enter, waiting for navigation...")
                time.sleep(5)
                
                print("URL after search:", page.url)
                page.screenshot(path="scratch/adata_after_search.png")
                
                # Check for links or results
                results = page.query_selector_all("a[href^='/c/']") or page.query_selector_all("a[href*='/company/']") or page.query_selector_all("a.search-result-link") or page.query_selector_all(".search-results a")
                print(f"Found {len(results)} potential result links.")
                for i, r in enumerate(results[:10]):
                    print(f"Result {i+1}: {r.inner_text().strip()} -> {r.get_attribute('href')}")
            else:
                print("No search input found.")
                
        except Exception as e:
            print("Error occurred:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test_adata_search("ии")
