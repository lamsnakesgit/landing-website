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
        
        print("[*] Открываем главную страницу...")
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
                    
                    print("Текущий URL:", page.url)
                    
                    # Найдем все элементы, содержащие текст "Открыть карточку"
                    card_triggers = page.locator("*:has-text('Открыть карточку')")
                    print(f"Элементов с текстом 'Открыть карточку': {card_triggers.count()}")
                    for i in range(min(10, card_triggers.count())):
                        el = card_triggers.nth(i)
                        tag = el.evaluate("node => node.tagName")
                        text = el.evaluate("node => node.textContent")
                        href = el.evaluate("node => node.getAttribute('href') || node.getAttribute('to') || ''")
                        classes = el.evaluate("node => node.className")
                        print(f"Элемент {i}: tag={tag}, text='{text.strip()}', href='{href}', class='{classes[:100]}'")
                        
                    # Также сохраним HTML всей секции результатов, чтобы исследовать структуру
                    results_block = page.locator("main")
                    if results_block.count() > 0:
                        html = results_block.first.inner_html()
                        with open("scratch/search_results_main.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        print("[+] Успешно сохранили main-секцию в scratch/search_results_main.html")
                    else:
                        print("[-] Секция main не найдена.")
        browser.close()

if __name__ == "__main__":
    main()
