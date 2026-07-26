import time
from playwright.sync_api import sync_playwright

def dump_links():
    print("Dumping links from adata.kz homepage...")
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
            page.goto("https://adata.kz/", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            links = page.query_selector_all("a")
            print(f"Found {len(links)} links on the homepage:")
            for i, link in enumerate(links):
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                if href:
                    print(f"Link {i+1}: {text} -> {href}")
                    
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    dump_links()
