import os
import re
import sys
import json
import subprocess
import html as html_lib
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3
import ddddocr
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://office.sud.kz"
OUTPUT_FILE = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/labor_cases.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,kk;q=0.8",
}

def sign_xml(xml_string: str) -> str:
    """Подписывает XML строку через kalkan_sign внутри Docker-контейнера."""
    # Сохраняем во временный файл
    tmp_path = "/tmp/unsigned.xml"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(xml_string)
    
    # Копируем файл в контейнер
    subprocess.run(["docker", "cp", tmp_path, "kalkan_parser:/root/ai_lawyer/unsigned.xml"], check=True)
    
    # Вызываем C-утилиту внутри контейнера
    print("✍️  Вызываем kalkan_sign в Docker...")
    res = subprocess.run([
        "docker", "exec", "kalkan_parser",
        "/root/ai_lawyer/kalkan_sign",
        "/root/ai_lawyer/cert.p12",
        "Prioritize_resource3!",
        "/root/ai_lawyer/unsigned.xml"
    ], capture_output=True, text=True)
    
    if res.returncode != 0:
        raise RuntimeError(f"Ошибка подписания: {res.stdout}\n{res.stderr}")
    
    out = res.stdout
    if "Signed XML:" in out:
        return out.split("Signed XML:")[1].strip()
    return out.strip()


def get_login_page(session: requests.Session) -> dict:
    """GET главной страницы — получаем ViewState, JSESSIONID и XML для подписи."""
    print("📡 GET index.xhtml ...")
    resp = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Извлекаем XML для подписания
    xml_match = re.search(r'id="xmlToSign0"[^>]*value="([^"]+)"', html)
    if not xml_match:
        raise RuntimeError("Не найден xmlToSign0 на странице логина")
    xml_to_sign = html_lib.unescape(xml_match.group(1))
    print(f"  📄 XML для подписи получен (UUID: {xml_to_sign[-50:].strip()})")

    # ViewState
    vs_match = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html)
    view_state = vs_match.group(1) if vs_match else ""

    signed_field_match = re.search(r'name="(j_idt[^"]*signedXml)"', html)
    signed_field = signed_field_match.group(1) if signed_field_match else ""

    if signed_field:
        parts = signed_field.split(":")
        eds_form = f"{parts[0]}:{parts[1]}"
    else:
        eds_form = ""

    ajax_btn_match = re.search(r'RichFaces\.ajax\("([^"]+)"', html)
    ajax_btn_id = ajax_btn_match.group(1) if ajax_btn_match else ""

    return {
        "xml_to_sign": xml_to_sign,
        "view_state": view_state,
        "signed_field": signed_field,
        "eds_form": eds_form,
        "ajax_btn_id": ajax_btn_id,
    }


def login_with_eds(session: requests.Session, page_data: dict) -> bool:
    signed_xml = sign_xml(page_data["xml_to_sign"])
    
    eds_form = page_data["eds_form"]
    ajax_btn  = page_data["ajax_btn_id"]
    signed_field = page_data["signed_field"]
    view_state   = page_data["view_state"]

    payload = {
        eds_form: eds_form,
        signed_field: signed_xml,
        "javax.faces.ViewState": view_state,
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": ajax_btn,
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        ajax_btn: ajax_btn,
    }

    ajax_headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Faces-Request": "partial/ajax",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/index.xhtml",
    }

    print("📡 RichFaces AJAX авторизация ...")
    resp = session.post(f"{BASE_URL}/index.xhtml", data=payload, headers=ajax_headers, timeout=30)
    
    check = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    if "Шығу" in check.text or "Выход" in check.text or "Сот кабинеті" in check.text:
        print("  ✅ Авторизация успешна!")
        return True
    return False

def solve_captcha(session: requests.Session) -> str:
    """Скачивает и решает капчу с помощью ddddocr"""
    print("  🖼 Скачиваем капчу...")
    resp = session.get(f"{BASE_URL}/img/captcha.jpg", headers=HEADERS)
    
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.classification(resp.content)
    print(f"  🤖 Капча распознана: {res}")
    return res


def search_and_download_cases(session: requests.Session):
    print("🔍 Открываем Банк судебных актов...")
    resp = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)
    
    view_state_match = re.search(r'id="j_id1:javax.faces.ViewState:\d+"\s+value="([^"]+)"', resp.text)
    if not view_state_match:
        print("❌ Не найден ViewState для поиска")
        return []
    view_state = view_state_match.group(1)
    
    category_id = "142030000100000000" # Трудовые споры
    print(f"📡 Отправляем запрос на поиск (Трудовые споры)...")
    
    ajax_headers = HEADERS.copy()
    ajax_headers["Faces-Request"] = "partial/ajax"
    ajax_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    
    data = {
        "j_idt35:j_idt40:j_idt41": "j_idt35:j_idt40:j_idt41",
        "javax.faces.ViewState": view_state,
        "j_idt35:j_idt40:j_idt41:edit-category": category_id,
        "j_idt35:j_idt40:j_idt41:edit-period": "2024",
        "j_idt35:j_idt40:j_idt41:edit-participantTypeCheckbox": "FIRSTINSTANCE",
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt35:j_idt40:j_idt41:j_idt138",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        "j_idt35:j_idt40:j_idt41:j_idt138": "j_idt35:j_idt40:j_idt41:j_idt138"
    }
    
    resp_search = session.post(f"{BASE_URL}/form/courtActs/index.xhtml", headers=ajax_headers, data=data)
    
    resp_results = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS)
    html_soup = BeautifulSoup(resp_results.text, "html.parser")
    
    view_state_input = html_soup.find("input", {"name": "javax.faces.ViewState"})
    if view_state_input:
        view_state = view_state_input.get("value")
        
    cases = []
    rows = html_soup.find_all('tr', {'onclick': lambda x: x and 'viewSelectedLawsuit' in x})
        
    for idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 3:
            clean_cells = [c.get_text(strip=True) for c in cells]
            if any("Медиация" in c for c in clean_cells):
                continue
                
            case_data = {
                "data": clean_cells,
                "docs": []
            }
            
            onclick = row.get('onclick', '')
            param1 = str(idx)
            m = re.search(r"viewSelectedLawsuit\('([^']+)'\)", onclick)
            if m:
                param1 = m.group(1)
                
            print(f"  Fetching details for case param1={param1}...")
            data_case = {
                "j_idt33:j_idt111": "j_idt33:j_idt111",
                "javax.faces.ViewState": view_state,
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "j_idt33:j_idt111:j_idt112",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "@all",
                "j_idt33:j_idt111:j_idt112": "j_idt33:j_idt111:j_idt112",
                "param1": param1
            }
            session.post(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=ajax_headers, data=data_case)
            
            resp_docs = session.get(f"{BASE_URL}/form/courtActs/documentList.xhtml", headers=HEADERS)
            doc_soup = BeautifulSoup(resp_docs.text, "html.parser")
            
            # Находим ссылки на скачивание
            # Обычно это <a href="#" onclick="downloadSelectedDoc(X, Y); return false;">
            docs_found = doc_soup.find_all('a', {'onclick': lambda x: x and 'downloadSelectedDoc' in x})
            
            doc_view_state_input = doc_soup.find("input", {"name": "javax.faces.ViewState"})
            doc_view_state = doc_view_state_input.get("value") if doc_view_state_input else view_state
            
            for doc_a in docs_found:
                doc_name = doc_a.get_text(strip=True)
                doc_onclick = doc_a.get('onclick', '')
                doc_m = re.search(r"downloadSelectedDoc\('?([^',]+)'?,\s*'?([^',]+)'?\)", doc_onclick)
                if doc_m:
                    d_p1 = doc_m.group(1)
                    d_p2 = doc_m.group(2)
                    print(f"  📄 Найден документ: {doc_name} (p1={d_p1}, p2={d_p2})")
                    
                    # 1. Триггерим открытие модалки капчи
                    data_prep_doc = {
                        "j_idt33:j_idt36:j_idt61": "j_idt33:j_idt36:j_idt61",
                        "javax.faces.ViewState": doc_view_state,
                        "javax.faces.partial.ajax": "true",
                        "javax.faces.source": "j_idt33:j_idt36:j_idt61:j_idt62",
                        "javax.faces.partial.execute": "@all",
                        "javax.faces.partial.render": "@all",
                        "j_idt33:j_idt36:j_idt61:j_idt62": "j_idt33:j_idt36:j_idt61:j_idt62",
                        "param1": d_p1,
                        "param2": d_p2
                    }
                    resp_prep = session.post(f"{BASE_URL}/form/courtActs/documentList.xhtml", headers=ajax_headers, data=data_prep_doc)
                    
                    # Извлекаем новый ViewState (JSF часто его обновляет)
                    prep_vs_m = re.search(r'id="j_id1:javax.faces.ViewState:\d+"\s+value="([^"]+)"', resp_prep.text)
                    if prep_vs_m:
                        doc_view_state = prep_vs_m.group(1)
                    
                    # 2. Решаем капчу
                    captcha_val = solve_captcha(session)
                    
                    # 3. Сабмитим капчу
                    data_captcha = {
                        "j_idt33:j_idt36:captchaForm": "j_idt33:j_idt36:captchaForm",
                        "javax.faces.ViewState": doc_view_state,
                        "j_idt33:j_idt36:captchaForm:edit-captcha": captcha_val,
                        "javax.faces.partial.ajax": "true",
                        "javax.faces.source": "j_idt33:j_idt36:captchaForm:downloadDocBtn",
                        "javax.faces.partial.execute": "@all",
                        "javax.faces.partial.render": "@all",
                        "j_idt33:j_idt36:captchaForm:downloadDocBtn": "j_idt33:j_idt36:captchaForm:downloadDocBtn"
                    }
                    resp_cap = session.post(f"{BASE_URL}/form/courtActs/documentList.xhtml", headers=ajax_headers, data=data_captcha)
                    
                    # Проверяем, прошла ли капча. В успешном ответе будет обновление hideDownloadLinkPanel с параметрами "n" и "u"
                    n_val = None
                    u_val = None
                    # Парсим ответ
                    n_m = re.search(r'name="n"[^>]*value="([^"]+)"', resp_cap.text)
                    u_m = re.search(r'name="u"[^>]*value="([^"]+)"', resp_cap.text)
                    if n_m and u_m:
                        n_val = html_lib.unescape(n_m.group(1))
                        u_val = html_lib.unescape(u_m.group(1))
                        print(f"  ✅ Капча пройдена! file_id: {n_val}")
                        
                        # 4. Скачиваем сам файл
                        download_data = {
                            "n": n_val,
                            "u": u_val,
                            "page": "/courtActs/documentList",
                            "b64": "none",
                            "inline": ""
                        }
                        resp_pdf = session.post(f"{BASE_URL}/ticket/fileDownload", data=download_data, headers=HEADERS)
                        if resp_pdf.status_code == 200:
                            os.makedirs("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/pdfs", exist_ok=True)
                            safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', doc_name)
                            pdf_path = f"/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/pdfs/{param1}_{safe_name}.pdf"
                            with open(pdf_path, "wb") as f:
                                f.write(resp_pdf.content)
                            print(f"  💾 Файл сохранен: {pdf_path}")
                            case_data['docs'].append(pdf_path)
                        else:
                            print(f"  ❌ Ошибка скачивания PDF: {resp_pdf.status_code}")
                    else:
                        print(f"  ❌ Капча не подошла (или файл недоступен)!")
                        
            resp_back = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS)
            back_soup = BeautifulSoup(resp_back.text, "html.parser")
            back_vs = back_soup.find("input", {"name": "javax.faces.ViewState"})
            if back_vs:
                view_state = back_vs.get("value")
                
            cases.append(case_data)
            
            # Сохраняем после каждого дела
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
                
    print(f"📊 Обработано дел: {len(cases)}")
    return cases


def main():
    print("==================================================")
    print("  ПАРСЕР СУДЕБНЫХ ДЕЛ + КАПЧА — MAC LOCAL")
    print("==================================================")

    session = requests.Session()
    session.verify = False
    
    page_data = get_login_page(session)
    if not page_data:
        return

    if login_with_eds(session, page_data):
        search_and_download_cases(session)
        print("\n✅ Готово!")

if __name__ == "__main__":
    main()
