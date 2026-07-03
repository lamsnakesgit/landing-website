import json
import time
from playwright.sync_api import sync_playwright

def get_auth_cookies():
    print("🚀 Запуск stealth-браузера для обхода защиты...")
    with sync_playwright() as p:
        # Запускаем видимый браузер, чтобы юрист мог выбрать ЭЦП
        browser = p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("🌐 Открываем Судебный кабинет (office.sud.kz)...")
        page.goto("https://office.sud.kz/")
        
        print("⏳ Ждем авторизации... Нажми 'Войти', выбери ЭЦП и введи пароль в NCALayer.")
        print("У тебя есть 2 минуты (120 секунд).")
        
        # Ждем, пока пользователь залогинится (можно проверять по появлению элемента профиля, 
        # но для надежности просто даем время)
        time_elapsed = 0
        while time_elapsed < 120:
            try:
                content = page.content()
                if "Шығу" in content or "Выход" in content:
                    print("✅ Успешная авторизация обнаружена!")
                    break
            except Exception:
                # Игнорируем ошибку навигации (Unable to retrieve content)
                pass
            time.sleep(2)
            time_elapsed += 2
            
        print("🍪 Сохраняем сессионные данные (Cookies + LocalStorage)...")
        context.storage_state(path="sud_state.json")
            
        print("✅ Сессия успешно сохранена в sud_state.json!")
        print("Браузер закрывается. Дальше работает parser_tk.py в фоне.")
        browser.close()

if __name__ == "__main__":
    get_auth_cookies()
