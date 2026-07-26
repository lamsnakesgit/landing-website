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
                    
                    # Ищем точные совпадения элементов
                    print("[*] Ищем кнопки 'Открыть карточку'...")
                    
                    # Найдем все элементы, у которых textContent ровно равен "Открыть карточку" (или содержит, но без дочерних)
                    # В xpath это: //*[text()='Открыть карточку'] или //*[contains(text(), 'Открыть карточку')]
                    card_buttons = page.locator("//*[text()='Открыть карточку' or normalize-space(.)='Открыть карточку']")
                    cnt = card_buttons.count()
                    print(f"[+] Найдено точных элементов: {cnt}")
                    for i in range(min(5, cnt)):
                        el = card_buttons.nth(i)
                        tag = el.evaluate("node => node.tagName")
                        href = el.evaluate("node => node.getAttribute('href') || node.getAttribute('to') || ''")
                        classes = el.evaluate("node => node.className")
                        onclick = el.evaluate("node => node.getAttribute('onclick') || ''")
                        
                        # Найдем родителя, чтобы понять контекст
                        parent_info = el.locator("..").evaluate("node => ({tag: node.tagName, class: node.className, html: node.innerHTML})")
                        
                        print(f"Элемент {i}: tag={tag}, class='{classes}', href='{href}', onclick='{onclick}'")
                        print(f"  Родитель: tag={parent_info['tag']}, class='{parent_info['class']}'")
                        print(f"  Родитель HTML (кусок): {parent_info['html'][:300]}")
                        
        browser.close()

if __name__ == "__main__":
    main()
