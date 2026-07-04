import os
import re
import requests
import html as html_lib
import subprocess
from bs4 import BeautifulSoup
import sys
import json
import time

BASE_URL = "https://office.sud.kz"
KEY_PATH = "/keys"
SIGN_BIN = "/app/kalkan_sign"
ECP_PASS = os.environ.get("ECP_PASSWORD", "Prioritize_resource3!")
DATA_DIR = "/data"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}

TARGET_CATEGORIES = {
    "142040000300010000": "Об оспаривании действий ЧСИ",
    "142030003000000000": "Корпоративные споры",
    "142030001200070000": "По договору подряда"
}

def find_key():
    for f in os.listdir(KEY_PATH):
        if f.startswith("GOST") and f.endswith(".p12"):
            return os.path.join(KEY_PATH, f)
    raise FileNotFoundError("Ключ не найден")

def sign_xml(xml_string):
    key = find_key()
    result = subprocess.run([SIGN_BIN, key, ECP_PASS, xml_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()

def do_auth(session):
    import time
    for attempt in range(5):
        try:
            resp = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=60)
            html = resp.text
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
            
            session.post(f"{BASE_URL}/index.xhtml", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Faces-Request": "partial/ajax"}, timeout=60)
            return True
        except Exception as e:
            print(f"❌ Ошибка авторизации (попытка {attempt+1}): {e}")
            time.sleep(5)
    return False

def search_category(session, category_code, category_name, year, page=1):
    for attempt in range(5):
        try:
            print(f"📡 Запрашиваем: {category_name} ({category_code}) за {year} год (стр. {page}). Попытка {attempt+1}...")
            resp_index = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS, timeout=60)
            view_state_match = re.search(r'id="j_id1:javax.faces.ViewState:\d+"\s+value="([^"]+)"', resp_index.text)
            if not view_state_match:
                view_state_match = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', resp_index.text)
            view_state = view_state_match.group(1)
            
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
                "j_idt35:j_idt40:j_idt41:edit-category": category_code,
                "j_idt35:j_idt40:j_idt41:edit-period": year,
                "javax.faces.ViewState": view_state
            }
            
            resp_search = session.post(f"{BASE_URL}/form/courtActs/index.xhtml", headers=ajax_headers, data=data, timeout=60)
            resp_list = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS, timeout=60)
            
            html_soup = BeautifulSoup(resp_list.text, "html.parser")
            rows = html_soup.find_all('tr', {"onclick": lambda x: x and "viewSelectedLawsuit" in x})
            cases = []
            for row in rows:
                cells = row.find_all(['td', 'th'])
                clean_cells = [c.get_text(strip=True) for c in cells]
                if any(clean_cells):
                    cases.append(clean_cells)
            return cases
        except Exception as e:
            print(f"⚠️ Ошибка сети: {e}. Ждем 10 секунд...")
            time.sleep(10)
            
    print(f"❌ Не удалось скачать {category_name} после 5 попыток.")
    return []

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    session = requests.Session()
    session.verify = False
    import urllib3
    urllib3.disable_warnings()

    print("🔑 Авторизация...")
    if not do_auth(session):
        return
    print("✅ Авторизация успешна!")

    years = ["2024", "2023"]
    
    for year in years:
        year_dir = os.path.join(DATA_DIR, year)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
            
        for cat_code, cat_name in TARGET_CATEGORIES.items():
            safe_name = re.sub(r'[\\/*?:"<>|]', "", cat_name)[:100]
            file_name = f"{safe_name}_{cat_code}.json"
            file_path = os.path.join(year_dir, file_name)
            
            cases = search_category(session, cat_code, cat_name, year)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cases, f, ensure_ascii=False, indent=4)
                
            print(f"✅ Сохранено дел: {len(cases)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
