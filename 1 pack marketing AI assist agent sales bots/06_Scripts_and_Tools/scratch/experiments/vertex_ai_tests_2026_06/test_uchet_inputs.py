from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://pk.uchet.kz/search/")
    inputs = page.evaluate("() => Array.from(document.querySelectorAll('input')).map(i => ({name: i.name, placeholder: i.placeholder, id: i.id, class: i.className}))")
    print(inputs)
    browser.close()
