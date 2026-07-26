from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://2gis.kz/almaty/search/Мебель на заказ")
    page.wait_for_timeout(3000)
    with open("2gis_dump.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    browser.close()
