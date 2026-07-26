import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Переходим к поиску
        company = "Стройшахтопроект"
        print(f"[*] Ищем '{company}' на pk.uchet.kz...")
        page.goto(f"https://pk.uchet.kz/search/nab/?query={company}", wait_until="networkidle")
        time.sleep(3)
        
        # Получаем первую ссылку на компанию
        first_link = page.query_selector("a[href^='/c/']")
        if first_link:
            href = first_link.get_attribute("href")
            company_url = f"https://pk.uchet.kz{href}"
            print(f"[+] Найдена компания: {first_link.inner_text().strip()} -> {company_url}")
            
            # Переходим в карточку компании
            page.goto(company_url, wait_until="networkidle")
            time.sleep(3)
            
            # Записываем текст страницы
            text = page.inner_text("body")
            print("=== ТЕКСТ СТРАНИЦЫ (первые 1000 символов) ===")
            print(text[:1500])
            
            # Сохраняем полный dump для анализа
            with open("scratch/uchet_card_dump.txt", "w", encoding="utf-8") as f:
                f.write(text)
        else:
            print("[-] Компания не найдена в результатах поиска.")
            
        browser.close()

if __name__ == "__main__":
    main()
