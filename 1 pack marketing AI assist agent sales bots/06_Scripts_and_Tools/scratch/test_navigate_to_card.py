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
                    
                    print("Текущий URL после поиска:", page.url)
                    
                    # Найдем все article
                    articles = page.locator("article")
                    cnt = articles.count()
                    print(f"Найдено карточек: {cnt}")
                    
                    # Выберем первый действующий Казахтелеком (обычно индекс 2)
                    target_idx = -1
                    for i in range(cnt):
                        text = articles.nth(i).inner_text()
                        if "941240000193" in text: # БИН Казахтелекома головного
                            target_idx = i
                            break
                            
                    if target_idx != -1:
                        print(f"[+] Нашли целевую карточку на позиции {target_idx}. Кликаем 'Открыть карточку'...")
                        target_art = articles.nth(target_idx)
                        
                        # Находим кнопку "Открыть карточку" внутри этого article
                        btn = target_art.locator("button:has-text('Открыть карточку')").first
                        if btn.count() > 0:
                            # Кликаем по кнопке
                            page.evaluate("el => el.click()", btn.element_handle())
                            time.sleep(5) # Ждем загрузки карточки
                            
                            print("URL после перехода в карточку:", page.url)
                            print("Заголовок карточки:", page.title())
                            
                            # Извлекаем текст страницы компании
                            card_text = page.inner_text("body")
                            
                            # Попробуем найти налоги и размер предприятия в тексте
                            print("\n--- Результаты парсинга карточки ---")
                            # Поиск БИН/ИИН
                            import re
                            bin_match = re.search(r'(БИН|ИИН):?\s*(\d{12})', card_text, re.IGNORECASE)
                            print("БИН:", bin_match.group(2) if bin_match else "Не найден")
                            
                            # Поиск руководителя
                            lpr_match = re.search(r'Руководитель:?\s*([^\n]+)', card_text, re.IGNORECASE)
                            print("Руководитель:", lpr_match.group(1).strip() if lpr_match else "Не найден")
                            
                            # Поиск размера предприятия
                            size_match = re.search(r'Размер предприятия:?\s*([^\n]+)', card_text, re.IGNORECASE)
                            print("Размер предприятия:", size_match.group(1).strip() if size_match else "Не найден")
                            
                            # Поиск налогов
                            # Налоговые отчисления обычно выводятся таблицей или строкой. Поищем слово "Налог"
                            tax_matches = re.findall(r'.*налог.*', card_text, re.IGNORECASE)
                            print(f"Строк со словом 'налог' ({len(tax_matches)}):")
                            for tm in tax_matches[:5]:
                                print("  ", tm.strip())
                        else:
                            print("[-] Кнопка 'Открыть карточку' в этой статье не найдена.")
                    else:
                        print("[-] Целевой БИН не найден в результатах поиска.")
                        
        browser.close()

if __name__ == "__main__":
    main()
