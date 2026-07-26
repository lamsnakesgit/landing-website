#!/usr/bin/env python3
# Авторизация в Судебный Кабинет через QR-код (одноразовая ручная операция)
# После успешного входа куки сохраняются в /opt/ai_lawyer/session_cookies.json
# Последующие запросы используют куки без повторной авторизации

import asyncio
import json
from playwright.async_api import async_playwright

SESSION_FILE = '/opt/ai_lawyer/session_cookies.json'
QR_SCREENSHOT = '/opt/ai_lawyer/scripts/qr_code.png'

async def login_via_qr():
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

        print("[1] Переходим на страницу входа...")
        await page.goto("https://office.sud.kz/main", 
                        wait_until='domcontentloaded', timeout=30000)
        
        # Ищем кнопку входа / авторизации
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/opt/ai_lawyer/scripts/before_login.png')
        print(f"[1] URL: {page.url}")
        
        # Ищем кнопку "Войти" или "Кіру"
        login_selectors = [
            "text=Кіру", "text=Войти", "text=Вход",
            "a[href*='login']", "a[href*='auth']",
            ".login-btn", "#loginBtn",
            "button:has-text('Кіру')", "button:has-text('Войти')"
        ]
        
        for sel in login_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    print(f"[2] Нашли кнопку входа: {sel}")
                    await el.click()
                    await page.wait_for_timeout(2000)
                    break
            except:
                pass
        
        # Переходим сразу на страницу авторизации
        await page.goto("https://idp.egov.kz/idp/sign-in?redirectUrl=https://office.sud.kz/main",
                        wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/opt/ai_lawyer/scripts/login_page.png')
        print(f"[2] Страница входа: {page.url}")
        
        # Ищем вкладку QR
        qr_selectors = [
            "text=QR", "a[href*='qr']", ".qr-tab",
            "li:has-text('QR')", "button:has-text('QR')",
            "[data-tab='qr']"
        ]
        
        qr_found = False
        for sel in qr_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    print(f"[3] Нашли QR вкладку: {sel}")
                    await el.click()
                    await page.wait_for_timeout(2000)
                    qr_found = True
                    break
            except:
                pass
        
        if not qr_found:
            print("[3] QR вкладка не найдена, пробуем прямой URL...")
            # Показываем что есть на странице
            tabs = await page.query_selector_all('.nav-link, li, a, button')
            for tab in tabs[:20]:
                text = (await tab.inner_text()).strip()
                href = await tab.get_attribute('href') or ''
                if text:
                    print(f"    Элемент: '{text}' -> {href}")
        
        await page.screenshot(path=QR_SCREENSHOT)
        print(f"\n[4] QR-код сохранен: {QR_SCREENSHOT}")
        print("[!] ДЕЙСТВИЕ: Открой этот скриншот и отсканируй QR телефоном через eGov Mobile!")
        print("[!] Ждем 60 секунд пока ты сканируешь...")
        
        # Ждем успешной авторизации
        for i in range(12):  # 12 * 5 = 60 секунд
            await page.wait_for_timeout(5000)
            current_url = page.url
            print(f"[{(i+1)*5}s] URL: {current_url}")
            
            if "office.sud.kz" in current_url and "sign-in" not in current_url and "idp.egov" not in current_url:
                print("\n[SUCCESS] Авторизация прошла!")
                break
            
            await page.screenshot(path=f'/opt/ai_lawyer/scripts/wait_{i}.png')
        
        # Сохраняем куки сессии
        cookies = await context.cookies()
        with open(SESSION_FILE, 'w') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"\n[DONE] Куки сохранены в {SESSION_FILE}")
        print(f"[DONE] Финальный URL: {page.url}")
        await page.screenshot(path='/opt/ai_lawyer/scripts/final_state.png')
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_via_qr())
