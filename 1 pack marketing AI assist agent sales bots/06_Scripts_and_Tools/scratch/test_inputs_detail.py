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
        
        inputs = page.query_selector_all("input")
        print(f"[*] Начальное количество инпутов: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            placeholder = inp.get_attribute("placeholder") or ""
            inp_id = inp.get_attribute("id") or ""
            inp_type = inp.get_attribute("type") or ""
            inp_name = inp.get_attribute("name") or ""
            inp_class = inp.get_attribute("class") or ""
            print(f"  Input {idx}: id='{inp_id}', name='{inp_name}', type='{inp_type}', placeholder='{placeholder}', class='{inp_class[:50]}'")
            
        # Попробуем кликнуть по той кнопке, которая "Открыть поиск контрагента"
        # Ищем ее по aria-label или по тексту
        search_btn = page.locator("button[aria-label='Открыть поиск контрагента']").first
        if search_btn.count() > 0:
            print("[+] Найдена кнопка 'Открыть поиск контрагента'. Кликаем по ней через JS...")
            page.evaluate("btn => btn.click()", search_btn.element_handle())
            time.sleep(2)
            
            inputs_after = page.query_selector_all("input")
            print(f"[*] Количество инпутов после клика: {len(inputs_after)}")
            for idx, inp in enumerate(inputs_after):
                placeholder = inp.get_attribute("placeholder") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_type = inp.get_attribute("type") or ""
                inp_class = inp.get_attribute("class") or ""
                print(f"  Input {idx}: id='{inp_id}', type='{inp_type}', placeholder='{placeholder}', class='{inp_class[:50]}'")
        else:
            print("[-] Кнопка 'Открыть поиск контрагента' не найдена.")
            
        browser.close()

if __name__ == "__main__":
    main()
