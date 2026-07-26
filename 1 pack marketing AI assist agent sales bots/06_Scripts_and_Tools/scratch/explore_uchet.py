import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print("[*] Открываем pk.uchet.kz...")
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        
        # Запишем HTML для анализа
        html_content = page.content()
        with open("scratch/uchet_home_dump.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("Page title:", page.title())
        
        # Попробуем найти инпуты и кнопки
        inputs = page.query_selector_all("input")
        print(f"Total inputs: {len(inputs)}")
        for idx, i in enumerate(inputs):
            print(f"Input {idx}: id={i.get_attribute('id')}, name={i.get_attribute('name')}, placeholder='{i.get_attribute('placeholder')}', class='{i.get_attribute('class')}'")
            
        buttons = page.query_selector_all("button")
        print(f"Total buttons: {len(buttons)}")
        for idx, b in enumerate(buttons):
            print(f"Button {idx}: text='{b.inner_text().strip()}', id={b.get_attribute('id')}, class='{b.get_attribute('class')}'")
            
        # Попробуем ввести "Стройшахтопроект" в инпут поиска и отправить
        # Обычно поисковой инпут имеет placeholder со словом "поиск", "БИН" или "ИИН"
        search_input = None
        for i in inputs:
            placeholder = (i.get_attribute("placeholder") or "").lower()
            if "бин" in placeholder or "иин" in placeholder or "поиск" in placeholder or "название" in placeholder or "компани" in placeholder:
                search_input = i
                break
                
        if search_input:
            print("[+] Найден инпут для поиска!")
            search_input.fill("Стройшахтопроект")
            time.sleep(1)
            search_input.press("Enter")
            time.sleep(4)
            print("После поиска URL:", page.url)
            print("Новый заголовок страницы:", page.title())
            
            # Посмотрим ссылки на результаты
            links = page.query_selector_all("a")
            print(f"Total links after search: {len(links)}")
            for l in links[:30]:
                href = l.get_attribute("href")
                text = l.inner_text().strip()
                if href and ("bin" in href or "search" in href or "company" in href):
                    print(f"Link: {text} -> {href}")
        else:
            print("[-] Инпут для поиска не найден.")
            
        browser.close()

if __name__ == "__main__":
    main()
