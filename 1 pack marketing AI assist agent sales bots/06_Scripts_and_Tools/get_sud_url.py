from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(ignore_https_errors=True)
    page.goto("https://office.sud.kz/")
    page.wait_for_timeout(2000)
    
    # Try to find link to Bank of Court Acts
    links = page.locator("a")
    for i in range(links.count()):
        text = links.nth(i).text_content()
        href = links.nth(i).get_attribute("href")
        if text and "судебных актов" in text.lower():
            print(f"Found link: {text.strip()} -> {href}")
            
    # Take a screenshot to see what it looks like
    page.screenshot(path="office_sud.png")
    print("Screenshot saved to office_sud.png")
    
    browser.close()
