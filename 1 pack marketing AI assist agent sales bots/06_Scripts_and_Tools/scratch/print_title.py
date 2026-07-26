import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://pk.uchet.kz/search/nab/?query=Казахтелеком")
        time.sleep(3)
        print("Title:", page.title())
        print("URL:", page.url)
        content = page.content()
        print("HTML length:", len(content))
        browser.close()

if __name__ == "__main__":
    main()
