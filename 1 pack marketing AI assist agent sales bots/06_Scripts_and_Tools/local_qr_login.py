#!/usr/bin/env python3
import asyncio
import json
import subprocess
from playwright.async_api import async_playwright

VPS_IP = "151.241.100.226"
VPS_PASS = "r0oLNJP3xCO7O4SnL0bj"
COOKIES_FILE = "/tmp/sud_cookies.json"

async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("[1] Открываем office.sud.kz...")
        await page.goto("https://office.sud.kz/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Кликаем на таб "QR" прямо на странице судебного кабинета
        print("[2] Ищем вкладку 'QR'...")
        qr_tab = await page.query_selector("text=QR")
        if qr_tab:
            await qr_tab.click()
            print("[3] QR-код на экране Судебного кабинета! Открой eGov Mobile и сканируй ЕГО!")
        else:
            print("[!] Вкладка QR не найдена!")

        print("[!] Ждем завершения входа (до 3 минут)...")
        
        try:
            # Ждем появления кнопки Выход/Шығу
            await page.wait_for_selector("a[href*='logout'], a:has-text('Шығу'), a:has-text('Выйти')", timeout=180000)
            print(f"[SUCCESS] Успешный вход! Кнопка выхода найдена! Текущий URL: {page.url}")
            await page.wait_for_timeout(3000) 
        except Exception as e:
            print("[!] Таймаут. Вход не состоялся.")
            print(f"Текущий URL: {page.url}")

        cookies = await context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        sud_cookies = [c for c in cookies if "sud.kz" in c["domain"]]
        print(f"[4] Сохранено куки: {len(cookies)} (из них {len(sud_cookies)} для sud.kz)")

        await browser.close()

    print("\\n[5] Загружаем на VPS...")
    r = subprocess.run([
        "sshpass", "-p", VPS_PASS,
        "scp", "-o", "StrictHostKeyChecking=no",
        COOKIES_FILE,
        f"root@{VPS_IP}:/opt/ai_lawyer/session_cookies.json"
    ], capture_output=True, text=True)

    if r.returncode == 0:
        print("[DONE] Готово! Куки на VPS.")
    else:
        print(f"[ERROR] {r.stderr}")

if __name__ == "__main__":
    asyncio.run(login())
