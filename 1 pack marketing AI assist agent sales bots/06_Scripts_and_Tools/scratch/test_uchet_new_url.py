import time
from playwright.sync_api import sync_playwright

def try_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"[*] Testing URL: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(3)
            print("    Title:", page.title())
            print("    Actual URL:", page.url)
            print("    HTML length:", len(page.content()))
        except Exception as e:
            print("    Error:", e)
        browser.close()

if __name__ == "__main__":
    try_url("https://pk.uchet.kz/search/?query=Казахтелеком")
    try_url("https://pk.uchet.kz/search?query=Казахтелеком")
    try_url("https://pk.uchet.kz/search/?q=Казахтелеком")
    try_url("https://pk.uchet.kz/search?q=Казахтелеком")
