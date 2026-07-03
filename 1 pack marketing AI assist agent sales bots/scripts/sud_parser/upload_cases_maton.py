import os
import sys
import json
import requests
import time
from pathlib import Path

MATON_API_KEY = os.environ.get("MATON_API_KEY", "Tot5eHN_Tm2738fZjWPHQcMH9scggY7KXxztQJCjbpEEq5wP6PhXgweGRQHSUBKSQs4aAno7gRN9XgWtDCiogcaTOorsdcWxFuaMHFfo8A")
SHEET_ID = "13_tNfpK5lHJRYAaPGRktrH-zT0kZ1ZlgSIPs7f-l9AM"
BASE_URL = "https://gateway.maton.ai/google-drive"
SHEETS_URL = "https://gateway.maton.ai/google-sheets"

def create_folder(name, parent_id=None):
    url = f"{BASE_URL}/drive/v3/files"
    data = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id: data["parents"] = [parent_id]
    resp = requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}, json=data)
    if resp.status_code in (200, 201):
        return resp.json()["id"]
    return None

def upload_file(file_path, folder_id):
    url = f"{BASE_URL}/upload/drive/v3/files?uploadType=multipart"
    file_path = Path(file_path)
    if not file_path.exists(): return None
    
    metadata = {"name": file_path.name, "parents": [folder_id]}
    mime = "application/pdf" if file_path.suffix == ".pdf" else ("application/vnd.openxmlformats-officedocument.wordprocessingml.document" if file_path.suffix == ".docx" else "text/html")
    
    with open(file_path, "rb") as f:
        files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (file_path.name, f, mime)
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}"}, files=files)
    
    if resp.status_code in (200, 201):
        fid = resp.json()["id"]
        # Make public
        requests.post(f"{BASE_URL}/drive/v3/files/{fid}/permissions", 
                      headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"},
                      json={"role": "reader", "type": "anyone"})
        return f"https://drive.google.com/file/d/{fid}/view?usp=sharing"
    return None

def init_sheet():
    url = f"{SHEETS_URL}/v4/spreadsheets/{SHEET_ID}/values/Sheet1!A1:F1?valueInputOption=USER_ENTERED"
    data = {
        "values": [["Год", "Номер дела", "Стороны", "Оригинал (Суд Кабинет)", "Скриншот карточки (HTML)", "PDF Решение"]]
    }
    requests.put(url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}, json=data)

def append_row(row_data):
    url = f"{SHEETS_URL}/v4/spreadsheets/{SHEET_ID}/values/Sheet1!A:F:append?valueInputOption=USER_ENTERED"
    data = {"values": [row_data]}
    requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}, json=data)

def main():
    print("🚀 Начинаем загрузку дел в Google Drive & Sheets...")
    init_sheet()
    
    # Ищем файлы labor_cases_*.json
    base_dir = Path("/root/ai_lawyer/kalkan_docker/output")
    if not base_dir.exists():
        base_dir = Path(".")
        
    main_folder_id = create_folder("Судебные Дела (AI Lawyer)")
    if not main_folder_id:
        print("❌ Не удалось создать папку на GDrive")
        return

    processed = 0
    for year in range(2015, 2027):
        json_file = base_dir / f"labor_cases_{year}.json"
        if not json_file.exists(): continue
        
        print(f"Открываем {json_file.name}...")
        with open(json_file, "r") as f:
            cases = json.load(f)
            
        for case in cases:
            case_num = case["data"][0] if len(case["data"]) > 0 else "N/A"
            parties = case["data"][2] if len(case["data"]) > 2 else "N/A"
            param1 = case["param1"]
            original_url = f"https://office.sud.kz/form/courtActs/lawsuitList.xhtml?param1={param1}"
            
            pdf_link = "Нет файла"
            html_link = "Нет скриншота"
            
            docs = case.get("docs", [])
            for doc in docs:
                if doc.endswith(".pdf") or doc.endswith(".docx"):
                    pdf_path = base_dir / "pdfs" / Path(doc).name
                    if pdf_path.exists():
                        print(f"  Загружаем PDF: {pdf_path.name}")
                        res = upload_file(pdf_path, main_folder_id)
                        if res: pdf_link = res
            
            html_path = base_dir / "pdfs" / f"{year}_{case_num.replace('/', '_').replace(chr(92), '_')}_case.html"
            if html_path.exists():
                print(f"  Загружаем HTML: {html_path.name}")
                res = upload_file(html_path, main_folder_id)
                if res: html_link = res
                
            append_row([str(year), case_num, parties, original_url, html_link, pdf_link])
            processed += 1
            time.sleep(1)
            
    print(f"✅ Готово! Загружено {processed} дел.")

if __name__ == "__main__":
    main()
