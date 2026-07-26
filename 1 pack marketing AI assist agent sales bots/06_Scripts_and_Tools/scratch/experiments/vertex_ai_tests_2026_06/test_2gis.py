from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://2gis.kz/almaty/search/мебель")
    page.wait_for_selector("div[class*='_1h3cgic']", timeout=10000)
    print("Page loaded successfully.")
    browser.close()
