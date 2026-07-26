import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        
        search_btn = page.locator("button[aria-label='Открыть поиск контрагента']").first
        if search_btn.count() > 0:
            page.evaluate("btn => btn.click()", search_btn.element_handle())
            time.sleep(2)
            
            label = page.locator("label:has-text('Введите ИИН')").first
            if label.count() > 0:
                parent = label.locator("..")
                inp = parent.locator("input").first
                if inp.count() > 0:
                    inp.fill("Казахтелеком")
                    time.sleep(1)
                    inp.press("Enter")
                    time.sleep(5)
                    
                    articles = page.locator("article")
                    target_idx = -1
                    for i in range(articles.count()):
                        text = articles.nth(i).inner_text()
                        if "941240000193" in text:
                            target_idx = i
                            break
                            
                    if target_idx != -1:
                        target_art = articles.nth(target_idx)
                        btn = target_art.locator("button:has-text('Открыть карточку')").first
                        if btn.count() > 0:
                            page.evaluate("el => el.click()", btn.element_handle())
                            time.sleep(6) # Дадим больше времени на загрузку
                            
                            html_content = page.content()
                            with open("scratch/company_card.html", "w", encoding="utf-8") as f:
                                f.write(html_content)
                            print("[+] HTML сохранен в scratch/company_card.html")
                            
                            # Также выведем текстовое содержимое страницы, разбитое по строкам, чтобы посмотреть структуру
                            body_text = page.inner_text("body")
                            with open("scratch/company_card_text.txt", "w", encoding="utf-8") as f:
                                f.write(body_text)
                            print("[+] Текст сохранен в scratch/company_card_text.txt")
                            
        browser.close()

if __name__ == "__main__":
    main()
