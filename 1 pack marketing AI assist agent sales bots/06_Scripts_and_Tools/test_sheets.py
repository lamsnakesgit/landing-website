import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")
MATON_API_KEY = os.getenv("MATON_API_KEY")
HEADERS = {"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}

# 1. Create a Spreadsheet
url_create = "https://gateway.maton.ai/google-sheets/v4/spreadsheets"
data_create = {"properties": {"title": "Журнал Судебных Дел (Тест)"}}
resp_create = requests.post(url_create, headers=HEADERS, json=data_create)
if resp_create.status_code == 200:
    sheet_id = resp_create.json().get("spreadsheetId")
    print(f"✅ Создана таблица: {sheet_id}")
    
    # 2. Append a row
    url_append = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/A1:append?valueInputOption=USER_ENTERED"
    data_append = {
        "values": [
            ["Номер дела", "Стороны", "Суд", "Статус"]
        ]
    }
    resp_append = requests.post(url_append, headers=HEADERS, json=data_append)
    print(f"Append status: {resp_append.status_code}")
    print(resp_append.text)
else:
    print(f"❌ Ошибка: {resp_create.text}")
