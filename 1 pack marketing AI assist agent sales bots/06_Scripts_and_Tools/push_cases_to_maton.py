import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv(".env")
MATON_API_KEY = os.getenv("MATON_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {MATON_API_KEY}",
    "Content-Type": "application/json"
}

def create_sheet(title):
    url = "https://gateway.maton.ai/google-sheets/v4/spreadsheets"
    data = {"properties": {"title": title}}
    resp = requests.post(url, headers=HEADERS, json=data)
    return resp.json().get("spreadsheetId")

def append_rows(sheet_id, rows):
    url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/A1:append?valueInputOption=USER_ENTERED"
    data = {"values": rows}
    requests.post(url, headers=HEADERS, json=data)

def main():
    print("🚀 Начинаем выгрузку логов в Maton (Google Sheets)...")
    sheet_id = create_sheet("ИИ Юрист: Журнал Судебных Дел (Логи)")
    print(f"✅ Создана таблица логов! ID: {sheet_id}")
    
    # Заголовки
    append_rows(sheet_id, [["№ Дела", "Стороны", "Суд", "Статус", "Категория", "Дата выгрузки"]])
    
    json_path = "ai_lawyer_cases/labor_cases_2024.json"
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    
    print(f"📂 Загружаем {len(cases)} дел...")
    
    # Берем первые 50 для теста
    test_cases = cases[:50]
    
    batch = []
    for c in test_cases:
        data = c.get("data", [])
        if len(data) >= 5:
            batch.append([data[0], data[1], data[2], data[3], data[4], c.get("parsed_at", "")])
            
        # Загружаем пачками по 20 чтобы не спамить
        if len(batch) >= 20:
            append_rows(sheet_id, batch)
            batch = []
            time.sleep(1)
            
    if batch:
        append_rows(sheet_id, batch)
        
    print("\n🎉 Готово! Ссылка на журнал логов:")
    print(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

if __name__ == "__main__":
    main()
