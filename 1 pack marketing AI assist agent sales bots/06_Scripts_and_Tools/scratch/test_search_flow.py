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
        
        # Кликаем по кнопке поиска
        search_btn = page.locator("button[aria-label='Открыть поиск контрагента']").first
        if search_btn.count() > 0:
            print("[+] Найдена кнопка поиска. Кликаем...")
            page.evaluate("btn => btn.click()", search_btn.element_handle())
            time.sleep(2)
            
            # Находим инпут. Мы знаем, что у него label "Введите ИИН, БИН или название контрагента"
            # Попробуем найти input по label через relative selector или xpath
            print("[*] Ищем поле ввода...")
            search_input = None
            
            # Метод 1: поиск input рядом с label с нужным текстом
            label = page.locator("label:has-text('Введите ИИН')").first
            if label.count() > 0:
                print("[+] Найден label. Пробуем найти связанный input...")
                # Попробуем найти input в том же блоке
                parent = label.locator("..")
                inp = parent.locator("input").first
                if inp.count() > 0:
                    search_input = inp
                    print("[+] Найдено поле ввода через label!")
            
            # Метод 2 (резервный): найти все input и выбрать тот, у которого класс содержит appearance-none и он виден
            if not search_input:
                inputs = page.query_selector_all("input")
                for inp_el in inputs:
                    if inp_el.is_visible() and "appearance-none" in (inp_el.get_attribute("class") or ""):
                        # Убедимся, что это не форма поддержки (у формы поддержки плейсхолдер "Имя")
                        if (inp_el.get_attribute("placeholder") or "") == "":
                            search_input = page.locator(f"id={inp_el.get_attribute('id')}")
                            print(f"[+] Найдено поле ввода по классу! ID: {inp_el.get_attribute('id')}")
                            break
                            
            if search_input:
                # Вводим текст
                print("[*] Вводим 'Казахтелеком'...")
                search_input.fill("Казахтелеком")
                time.sleep(1)
                
                # Нажимаем Enter и ждем результатов
                print("[*] Отправляем запрос (Enter)...")
                search_input.press("Enter")
                time.sleep(5) # Даем время на загрузку результатов
                
                print("Текущий URL:", page.url)
                print("Текущий заголовок:", page.title())
                
                # Выводим ссылки результатов
                links = page.query_selector_all("a")
                print(f"Всего ссылок: {len(links)}")
                found_c = False
                for idx, l in enumerate(links):
                    href = l.get_attribute("href") or ""
                    text = l.inner_text().strip().replace("\n", " ")
                    if href.startswith("/c/") or "/c/" in href:
                        print(f"Результат: '{text}' -> {href}")
                        found_c = True
                if not found_c:
                    print("[-] Ссылки на компании не найдены. Содержимое body:")
                    print(page.inner_text("body")[:1000])
            else:
                print("[-] Поле ввода не найдено.")
        else:
            print("[-] Кнопка поиска не найдена.")
            
        browser.close()

if __name__ == "__main__":
    main()
