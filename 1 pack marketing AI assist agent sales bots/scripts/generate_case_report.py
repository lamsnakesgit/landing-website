import os
import json
import requests
from pathlib import Path

def load_env():
    env_path = Path("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

load_env()
MATON_API_KEY = os.environ.get("MATON_API_KEY")

def create_gdoc_from_html(html_content, doc_name):
    url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart"
    metadata = {
        "name": doc_name,
        "mimeType": "application/vnd.google-apps.document"
    }
    
    files = {
        "metadata": (None, json.dumps(metadata), "application/json"),
        "file": ("report.html", html_content, "text/html")
    }
    
    resp = requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}"}, files=files)
    if resp.status_code in (200, 201):
        doc_id = resp.json()["id"]
        perm_url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{doc_id}/permissions"
        requests.post(perm_url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}, json={"role": "reader", "type": "anyone"})
        return doc_id
    else:
        print(f"Error: {resp.text}")
        return None

def generate_report(case_data):
    # case_data format: list of strings from JSON 'data' field, plus 'param1', plus 'docs'
    case_num = case_data["data"][0] if len(case_data["data"]) > 0 else "N/A"
    date_reg = case_data["data"][1] if len(case_data["data"]) > 1 else "N/A"
    parties = case_data["data"][2] if len(case_data["data"]) > 2 else "N/A"
    judge = case_data["data"][3] if len(case_data["data"]) > 3 else "N/A"
    status = case_data["data"][4] if len(case_data["data"]) > 4 else "N/A"
    
    original_url = f"https://office.sud.kz/form/courtActs/lawsuitList.xhtml?param1={case_data.get('param1', '')}"
    
    # HTML template with embedded styling for beautiful Google Doc
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
            h3 {{ color: #3498db; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .info-table th, .info-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .info-table th {{ background-color: #f8f9fa; width: 30%; }}
            .docs-list {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #27ae60; }}
            .ai-analysis {{ background-color: #f4f6f7; padding: 15px; border-left: 4px solid #8e44ad; }}
        </style>
    </head>
    <body>
        <h1>Отчет AI Lawyer: Дело {case_num}</h1>
        <p><i>Сгенерировано автоматически системой AI Lawyer Assistant</i></p>
        
        <h3>1. Основная информация</h3>
        <table class="info-table">
            <tr><th>Номер дела</th><td>{case_num}</td></tr>
            <tr><th>Дата регистрации</th><td>{date_reg}</td></tr>
            <tr><th>Стороны</th><td>{parties}</td></tr>
            <tr><th>Судья</th><td>{judge}</td></tr>
            <tr><th>Статус</th><td>{status}</td></tr>
        </table>
        
        <h3>2. Ссылки и материалы</h3>
        <div class="docs-list">
            <p><b>Оригинал в Судебном кабинете:</b> <a href="{original_url}">Перейти к карточке дела</a></p>
            <p><b>Скриншот карточки дела:</b> [Будет вставлен скриншот при парсинге]</p>
            <p><b>Прикрепленные судебные акты:</b></p>
            <ul>
    """
    
    for doc in case_data.get("docs", []):
        html += f"<li>{doc.get('documentTitle', 'Документ')} ({doc.get('extension', 'N/A')})</li>"
        
    html += """
            </ul>
        </div>
        
        <h3>3. AI Анализ и Резюме (Gemini 1.5 Pro)</h3>
        <div class="ai-analysis">
            <p><b>Краткое изложение:</b> [Здесь будет summary от AI]</p>
            <p><b>Ключевые аргументы сторон:</b></p>
            <ul>
                <li>Истец ссылается на нарушение статьи...</li>
                <li>Ответчик парирует истечением сроков давности...</li>
            </ul>
            <p><b>Ошибки проигравшей стороны:</b> [Анализ ошибок]</p>
        </div>
    </body>
    </html>
    """
    
    print(f"Generating Doc for {case_num}...")
    doc_name = f"Дело {case_num} - Отчет AI"
    doc_id = create_gdoc_from_html(html, doc_name)
    if doc_id:
        print(f"✅ Успешно! Ссылка: https://docs.google.com/document/d/{doc_id}/edit")

if __name__ == "__main__":
    # Test with a dummy case to verify beautiful formatting
    sample_case = {
        "param1": "test-param-123",
        "data": [
            "7199-24-00-2/123",
            "10.05.2024",
            "Истец: ТОО АСТАНА. Ответчик: Иванов И.И.",
            "Судья: Петров П.П.",
            "Отказано (Выиграл ответчик)"
        ],
        "docs": [
            {"documentTitle": "Решение суда", "extension": "pdf"},
            {"documentTitle": "Определение о принятии", "extension": "docx"}
        ]
    }
    generate_report(sample_case)
