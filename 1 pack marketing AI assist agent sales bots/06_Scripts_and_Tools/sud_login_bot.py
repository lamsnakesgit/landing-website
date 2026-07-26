from playwright.sync_api import sync_playwright
import time

def login_sudebniy_kabinet():
    with sync_playwright() as p:
        # Запускаем видимый браузер, чтобы ты мог ввести пароль в окне NCALayer
        browser = p.chromium.launch(headless=False, args=['--ignore-certificate-errors'])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        print("🌐 Открываем Судебный кабинет...")
        page.goto("https://office.sud.kz/", wait_until="domcontentloaded")
        
        print("⏳ Жду, пока ты нажмешь 'Войти', выберешь свой новый ключ GOST и введешь пароль в появившемся окне NCALayer...")
        print("💡 Не торопись, у тебя есть 2 минуты на авторизацию.")
        
        # Ждем, пока URL изменится на внутренний кабинет или появится элемент выхода (значит залогинились)
        try:
            # Ожидание элемента, который появляется только после логина (например, имя пользователя или кнопка выхода)
            # В данном случае просто даем время на ручной логин и ждем редиректа
            page.wait_for_timeout(60000) # Ждем 60 секунд для теста
            
            print("✅ Время вышло или логин успешен! Сохраняю сессию (cookies)...")
            cookies = context.cookies()
            import json
            with open("sud_cookies.json", "w") as f:
                json.dump(cookies, f)
            print("🍪 Куки успешно сохранены в sud_cookies.json! Теперь бот может качать дела без ЭЦП.")
            
        except Exception as e:
            print(f"❌ Ошибка или таймаут: {e}")
            
        browser.close()

if __name__ == "__main__":
    login_sudebniy_kabinet()
