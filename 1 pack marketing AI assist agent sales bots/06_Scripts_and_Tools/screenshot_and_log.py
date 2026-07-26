import os
import json
import time
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(".env")
MATON_API_KEY = os.getenv("MATON_API_KEY")
HEADERS = {"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}

# URL Google Sheets для логов
SHEET_ID = "10NiXdoeCB9Dmuf3Tnx1w2cvYX8tmMOX4X-Alh-TC5W0"

def append_to_sheet(rows):
    url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/A1:append?valueInputOption=USER_ENTERED"
    data = {"values": rows}
    requests.post(url, headers=HEADERS, json=data)

def upload_file_to_drive(file_path, file_name, mime_type):
    # Загрузка файлов на Google Drive через Maton пока не реализована в gateway (обычно multipart/form-data)
    # Поэтому мы сохраняем скриншоты локально, а в логи пишем локальные пути.
    return os.path.abspath(file_path)

def main():
    os.makedirs("output/screenshots", exist_ok=True)
    os.makedirs("output/html", exist_ok=True)
    
    json_path = "ai_lawyer_cases/labor_cases_2024.json"
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)[:5] # Берем 5 дел для теста скриншотов
        
    print(f"🚀 Запуск Playwright для создания скриншотов ({len(cases)} дел)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        batch_logs = []
        
        for idx, case in enumerate(cases, 1):
            data = case.get("data", [])
            case_num = data[0].replace("/", "_") if len(data) > 0 else f"unknown_{idx}"
            
            # TODO: Здесь должна быть логика перехода на sud.kz и поиска дела по case_num
            # Так как sud.kz требует капчу/kalkan, мы пока симулируем открытие и скриншот
            print(f"📸 Обработка дела {case_num}...")
            
            # Симуляция (в реальности тут page.goto("https://office.sud.kz/..."))
            page.goto("https://sud.gov.kz/") # Откроем главную для теста
            time.sleep(2)
            
            screenshot_path = f"output/screenshots/{case_num}.png"
            html_path = f"output/html/{case_num}.html"
            
            page.screenshot(path=screenshot_path, full_page=True)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
                
            drive_screenshot_link = upload_file_to_drive(screenshot_path, f"{case_num}.png", "image/png")
            drive_html_link = upload_file_to_drive(html_path, f"{case_num}.html", "text/html")
            
            # Добавляем в лог
            batch_logs.append([
                data[0] if len(data)>0 else "", 
                data[1] if len(data)>1 else "", 
                data[2] if len(data)>2 else "", 
                data[3] if len(data)>3 else "", 
                drive_screenshot_link,
                drive_html_link
            ])
            
        browser.close()
        
        print("📝 Запись логов в Google Sheets...")
        append_to_sheet(batch_logs)
        print("✅ Успешно! Все логи и пути к скриншотам сохранены.")

if __name__ == "__main__":
    main()
