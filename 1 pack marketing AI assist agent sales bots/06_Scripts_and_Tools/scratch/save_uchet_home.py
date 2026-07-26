import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        html = page.content()
        with open("scratch/uchet_home_new.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()
        print("[+] Сохранено в scratch/uchet_home_new.html")

if __name__ == "__main__":
    main()
