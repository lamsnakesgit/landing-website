import os
import re
import requests
import html as html_lib
import subprocess
from bs4 import BeautifulSoup
import sys
import json
import urllib3

BASE_URL = "https://office.sud.kz"
KEY_PATH = "/keys"
SIGN_BIN = "/app/kalkan_sign"
ECP_PASS = os.environ.get("ECP_PASSWORD", "Prioritize_resource3!")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}

def find_key():
    for f in os.listdir(KEY_PATH):
        if f.startswith("GOST") and f.endswith(".p12"):
            return os.path.join(KEY_PATH, f)
    raise FileNotFoundError("Ключ не найден")

def sign_xml(xml_string):
    key = find_key()
    result = subprocess.run([SIGN_BIN, key, ECP_PASS, xml_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    return result.stdout.strip()

def search_global_cases(query: str, year: str = "2025"):
    session = requests.Session()
    session.verify = False
    urllib3.disable_warnings()

    # 1. Авторизация
    resp = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    html = resp.text
    try:
        xml_to_sign = html_lib.unescape(re.search(r'id="xmlToSign0"[^>]*value="([^"]+)"', html).group(1))
        view_state = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html).group(1)
        
        parts = re.search(r'name="(j_idt[^"]*signedXml)"', html).group(1).split(":")
        eds_form = f"{parts[0]}:{parts[1]}"
        signed_field = f"{parts[0]}:{parts[1]}:signedXml"

        signed_xml = sign_xml(xml_to_sign)
        payload = {
            eds_form: eds_form,
            signed_field: signed_xml,
            "javax.faces.ViewState": view_state,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": re.search(r'RichFaces\.ajax\("([^"]+)"', html).group(1),
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "@all",
        }
        payload[payload["javax.faces.source"]] = payload["javax.faces.source"]
        
        session.post(f"{BASE_URL}/index.xhtml", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Faces-Request": "partial/ajax"}, timeout=30)
    except Exception as e:
        return {"success": False, "error": f"Ошибка авторизации по ЭЦП: {str(e)}"}

    # 2. Переход к поиску
    resp_search = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)
    view_state_match = re.search(r'id="j_id1:javax.faces.ViewState:\d+"\s+value="([^"]+)"', resp_search.text)
    if not view_state_match:
        view_state_match = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', resp_search.text)
        if not view_state_match:
            return {"success": False, "error": "Не найден ViewState для формы поиска"}
    view_state = view_state_match.group(1)
    
    # 3. Отправка POST запроса поиска
    ajax_headers = HEADERS.copy()
    ajax_headers["Faces-Request"] = "partial/ajax"
    ajax_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    
    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt35:j_idt40:j_idt41:j_idt138",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        "j_idt35:j_idt40:j_idt41:j_idt138": "j_idt35:j_idt40:j_idt41:j_idt138",
        "j_idt35:j_idt40:j_idt41": "j_idt35:j_idt40:j_idt41",
        "j_idt35:j_idt40:j_idt41:edit-search": query,
        "j_idt35:j_idt40:j_idt41:edit-period": year,
        "javax.faces.ViewState": view_state
    }
    
    session.post(f"{BASE_URL}/form/courtActs/index.xhtml", headers=ajax_headers, data=data, timeout=30)
    
    # 4. Получение списка результатов
    resp_list = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS, timeout=30)
    html_soup = BeautifulSoup(resp_list.text, "html.parser")
    rows = html_soup.find_all('tr', {"onclick": lambda x: x and "viewSelectedLawsuit" in x})
    
    cases = []
    for idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        clean_cells = [c.get_text(strip=True) for c in cells]
        
        # Получаем ссылки на документы внутри строки, если они есть
        doc_links = []
        for a in row.find_all('a', href=True):
            doc_links.append(f"{BASE_URL}{a['href']}")
            
        if len(clean_cells) >= 6:
            cases.append({
                "row_index": idx,
                "case_number": clean_cells[0],
                "court": clean_cells[1],
                "category": clean_cells[2],
                "parties": clean_cells[3],
                "judge": clean_cells[4],
                "date": clean_cells[5] if len(clean_cells) > 5 else "",
                "result": clean_cells[6] if len(clean_cells) > 6 else "Рассматривается",
                "links": doc_links
            })
            
    return {"success": True, "cases": cases}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Не передан поисковый запрос (ИИН/БИН)"}))
        sys.exit(1)
        
    query_str = sys.argv[1]
    year_str = sys.argv[2] if len(sys.argv) > 2 else "2025"
    
    res = search_global_cases(query_str, year_str)
    print(json.dumps(res, ensure_ascii=False))
