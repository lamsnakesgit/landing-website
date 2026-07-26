#!/usr/bin/env python3
# Авторизация на eGov/Судебный Кабинет через ИИН + пароль (без ЭЦП и NCALayer)

import asyncio
from playwright.async_api import async_playwright

IIN = "000912600473"
PASSWORD = "cZ8aTQbuM!lf"

async def login_with_password():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Слушаем консоль
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        print("Переходим на страницу входа eGov...")
        await page.goto("https://idp.egov.kz/idp/sign-in?redirectUrl=https://office.sud.kz/main", 
                        wait_until="networkidle", timeout=30000)
        
        await page.screenshot(path="/opt/ai_lawyer/scripts/step1_login_page.png")
        print(f"URL: {page.url}")
        print("Скриншот: step1_login_page.png")

        # Ищем вкладку "Логин/Пароль" или "ИИН"
        print("Ищем вкладку входа по паролю...")
        
        # Попробуем разные селекторы для переключения на вкладку пароля
        password_tab_selectors = [
            "text=Логин и пароль",
            "text=По паролю",
            "text=Пароль",
            "[data-tab='login']",
            ".tab-password",
            "a[href*='password']",
            "button:has-text('Логин')",
            ".nav-tabs a:nth-child(2)",
            "li:has-text('Пароль')",
        ]
        
        tab_found = False
        for selector in password_tab_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"Нашли вкладку: {selector}")
                    await element.click()
                    await page.wait_for_timeout(1000)
                    tab_found = True
                    break
            except:
                pass
        
        if not tab_found:
            print("Вкладка пароля не найдена, проверяем структуру страницы...")
            # Печатаем все видимые текстовые элементы для отладки
            tabs = await page.query_selector_all(".nav-link, .tab, li a, button")
            for tab in tabs:
                text = await tab.inner_text()
                print(f"  Элемент: '{text.strip()}'")
        
        await page.screenshot(path="/opt/ai_lawyer/scripts/step2_after_tab.png")
        
        # Вводим ИИН
        print("Вводим ИИН...")
        iin_selectors = [
            "input[name='username']",
            "input[placeholder*='ИИН']",
            "input[placeholder*='логин']",
            "input[id*='iin']",
            "input[id*='login']",
            "input[type='text']:first-of-type",
        ]
        
        iin_entered = False
        for selector in iin_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.fill(IIN)
                    print(f"ИИН введен через: {selector}")
                    iin_entered = True
                    break
            except:
                pass
        
        if not iin_entered:
            print("ОШИБКА: Поле ИИН не найдено!")
        
        # Вводим пароль
        print("Вводим пароль...")
        pass_selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='ароль']",
        ]
        
        pass_entered = False
        for selector in pass_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.fill(PASSWORD)
                    print(f"Пароль введен через: {selector}")
                    pass_entered = True
                    break
            except:
                pass
        
        if not pass_entered:
            print("ОШИБКА: Поле пароля не найдено!")
        
        await page.screenshot(path="/opt/ai_lawyer/scripts/step3_credentials.png")
        
        # Нажимаем войти
        print("Нажимаем кнопку Войти...")
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Войти')",
            "button:has-text('Вход')",
            ".btn-login",
            "#signInButton",
        ]
        
        for selector in submit_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.click()
                    print(f"Нажали кнопку через: {selector}")
                    break
            except:
                pass
        
        # Ждем редиректа
        print("Ждем авторизации (10 сек)...")
        await page.wait_for_timeout(10000)
        
        await page.screenshot(path="/opt/ai_lawyer/scripts/step4_after_login.png")
        print(f"Финальный URL: {page.url}")
        
        if "office.sud.kz" in page.url or "egov.kz" in page.url and "sign-in" not in page.url:
            print("УСПЕХ! Авторизация прошла!")
        else:
            print("Авторизация не прошла, проверьте скриншоты")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_with_password())
