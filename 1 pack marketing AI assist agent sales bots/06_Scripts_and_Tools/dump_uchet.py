from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://pk.uchet.kz/search/")
    search_input = page.locator('input').first
    search_input.fill("ресторан")
    search_input.press('Enter')
    page.wait_for_timeout(5000)
    html = page.content()
    with open("uchet_dom.html", "w") as f:
        f.write(html)
    browser.close()
