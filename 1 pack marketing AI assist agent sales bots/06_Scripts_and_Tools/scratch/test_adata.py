import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        # Open a company page from the logs
        url = "https://pk.adata.kz/company/250440026494"
        print(f"Opening {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(5)
        
        body_text = page.inner_text("body")
        print("\n=== Body text excerpt ===")
        print(body_text[:1500])
        print("=== End of excerpt ===\n")
        
        # Save full body text
        with open("scratch/adata_body.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
            
        # Take a screenshot
        page.screenshot(path="scratch/adata_company.png")
        print("Screenshot saved to scratch/adata_company.png")
        
        browser.close()

if __name__ == "__main__":
    main()
