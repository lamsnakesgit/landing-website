import os
import glob
import requests
import json
import time

WEBHOOK_URL = os.environ.get("MATON_WEBHOOK_URL", "")

PDF_DIR = "output/pdfs"
JSON_FILE = "output/labor_cases.json"

def upload_file_to_maton(filepath, case_data):
    """Отправляет файл на вебхук Maton/n8n для загрузки в Google Drive"""
    if not WEBHOOK_URL:
        print("⚠️ Ошибка: MATON_WEBHOOK_URL не установлен.")
        return False
        
    print(f"Uploading {os.path.basename(filepath)}...")
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        data = {
            'case_num': case_data.get('case_num', ''),
            'year': case_data.get('date', '')[:4],
            'judge': case_data.get('judge', ''),
            'plaintiff': case_data.get('plaintiff', ''),
            'defendant': case_data.get('defendant', ''),
            'court_url': "https://office.sud.kz" # Оригинальная ссылка
        }
        
        for attempt in range(3):
            try:
                response = requests.post(WEBHOOK_URL, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    print(f"✅ Успешно загружен: {filepath}")
                    return True
                else:
                    print(f"❌ Ошибка {response.status_code}: {response.text}")
            except Exception as e:
                print(f"⚠️ Ошибка сети при загрузке: {e}")
            time.sleep(2)
            
    return False

def main():
    if not os.path.exists(PDF_DIR):
        print(f"Папка {PDF_DIR} не найдена.")
        return
        
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            cases = json.load(f)
    except FileNotFoundError:
        cases = []
        
    case_map = {c.get("case_num", "").replace('/', '_'): c for c in cases}
    
    # Ищем все файлы (HTML, DOCX, PDF)
    all_files = glob.glob(os.path.join(PDF_DIR, "*.*"))
    
    for filepath in all_files:
        filename = os.path.basename(filepath)
        # Имя файла: YEAR_CASE-NUM_...
        parts = filename.split('_')
        case_data = {}
        if len(parts) > 1:
            # Пытаемся найти метаданные по case_num (parts[1] или склеенные части)
            # Это упрощенный поиск, в идеале лучше вытягивать case_num точнее
            for c_id, c_data in case_map.items():
                if c_id in filename:
                    case_data = c_data
                    break
        
        success = upload_file_to_maton(filepath, case_data)
        
        # Удаляем файл после успешной загрузки (Экономия места)
        if success:
            os.remove(filepath)
            print(f"🗑 Удалили локальный файл: {filepath}")

if __name__ == "__main__":
    main()
