"""
Парсер судебных дел с office.sud.kz через нативную подпись ЭЦП (KalkanCrypt).
Схема:
  1. GET index.xhtml -> получаем JSESSIONID, ViewState, xmlToSign (UUID)
  2. Декодируем XML и подписываем через kalkan_sign (C-wrapper)
  3. POST index.xhtml с подписанным XML -> получаем авторизованную сессию
  4. Ищем дела по категории, обходим все страницы, скачиваем PDF
"""
import os
import re
import sys
import time
import urllib3
import ddddocr
from bs4 import BeautifulSoup
import json
import subprocess
import html as html_lib
import requests
from datetime import datetime
import csv
from typing import Optional

KEY_PATH = "/keys"
SIGN_BIN = "/app/kalkan_sign"
ECP_PASS = os.environ.get("ECP_PASSWORD", "Prioritize_resource3!")
BASE_URL = "https://office.sud.kz"
YEAR = os.environ.get("PARSE_YEAR", "2026")
MATON_API_KEY = os.environ.get("MATON_API_KEY", "")

OUTPUT_FILE = f"/output/cases_{YEAR}.json"
LABOR_CASES_FILE = f"/output/labor_cases_{YEAR}.json"
PDF_DIR = "/output/pdfs"
DOWNLOAD_LOG_CSV = f"/output/download_log_{YEAR}.csv"

# Задержка между скачиваниями (сек) — защита от блокировки по IP
DOWNLOAD_DELAY = 2

# Глобальный буфер для сообщений в Telegram
tg_links_buffer = []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,kk;q=0.8",
}

AJAX_HEADERS = {
    **HEADERS,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Faces-Request": "partial/ajax",
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/form/courtActs/lawsuitList.xhtml",
}

def send_tg_message(text: str):
    bot_token = os.environ.get("ANTIGRAVITY_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID_MAIN")
    if bot_token and chat_id:
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)
        except Exception as e:
            print(f"TG Error: {e}")

def log_to_csv(case_num, category, file_path, gdrive_link):
    """Логируем в локальный CSV файл на VPS"""
    file_exists = os.path.isfile(DOWNLOAD_LOG_CSV)
    with open(DOWNLOAD_LOG_CSV, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Дата", "Номер дела", "Категория", "Локальный путь", "Google Drive Ссылка"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), case_num, category, file_path, gdrive_link])

# --- Maton AI Google Drive Integration ---
def create_folder(name, parent_id=None):
    """Создание папки на Google Drive через maton.ai"""
    if not MATON_API_KEY:
        return None
    url = "https://gateway.maton.ai/google-drive/drive/v3/files"
    data = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        data["parents"] = [parent_id]
    
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {MATON_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data,
        timeout=30
    )
    if resp.status_code in [200, 201]:
        return resp.json().get("id")
    print(f"⚠️ Ошибка создания папки GDrive '{name}': {resp.text}")
    return None

def upload_file_to_drive(file_path, folder_id=None, as_gdoc=False):
    """Загрузка файла на Google Drive через maton.ai.
       Если as_gdoc=True, файл конвертируется в Google Документ (OCR для PDF, конвертация для Word)."""
    if not MATON_API_KEY:
        return None
    url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files"
    
    metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        metadata["parents"] = [folder_id]
    
    # Конвертация в Google Docs
    if as_gdoc:
        metadata["mimeType"] = "application/vnd.google-apps.document"
    
    try:
        with open(file_path, "rb") as f:
            files = {
                "metadata": (None, json.dumps(metadata), "application/json"),
                "file": (os.path.basename(file_path), f, "application/octet-stream")
            }
            resp = requests.post(
                f"{url}?uploadType=multipart&fields=id,webViewLink",
                headers={"Authorization": f"Bearer {MATON_API_KEY}"},
                files=files,
                timeout=120
            )
            if resp.status_code == 200:
                return resp.json()
            print(f"⚠️ Ошибка загрузки файла в GDrive (as_gdoc={as_gdoc}): {resp.text}")
    except Exception as e:
        print(f"⚠️ Исключение при загрузке в GDrive: {e}")
    return None

def share_folder(folder_id):
    """Сделать папку доступной по ссылке (reader anyone)"""
    if not MATON_API_KEY:
        return None
    url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{folder_id}/permissions"
    data = {
        "role": "reader",
        "type": "anyone"
    }
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {MATON_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data,
        timeout=30
    )
    return resp.status_code == 200

def get_or_create_gdrive_structure(cat_name):
    """Создает структуру папок Банк судебных актов -> 2026 -> Категория
       И дублирующую структуру для Google Docs. Возвращает (original_cat_id, gdocs_cat_id)"""
    if not MATON_API_KEY:
        return None, None
    print("☁️ Подготовка папок в Google Drive...")
    
    # 1. Оригинальные файлы (PDF/Word)
    root_id = create_folder("Банк судебных актов")
    cat_id = None
    if root_id:
        share_folder(root_id)
        year_id = create_folder(YEAR, parent_id=root_id)
        if year_id:
            cat_id = create_folder(cat_name, parent_id=year_id)
            
    # 2. Конвертированные файлы (Google Docs)
    root_docs_id = create_folder("Банк судебных актов (Google Docs)")
    gdocs_cat_id = None
    if root_docs_id:
        share_folder(root_docs_id)
        year_docs_id = create_folder(YEAR, parent_id=root_docs_id)
        if year_docs_id:
            gdocs_cat_id = create_folder(cat_name, parent_id=year_docs_id)
            
    return cat_id, gdocs_cat_id
# ----------------------------------------


def find_key() -> str:
    """Ищет первый доступный GOST p12 ключ."""
    for f in os.listdir(KEY_PATH):
        if f.startswith("GOST") and f.endswith(".p12"):
            return os.path.join(KEY_PATH, f)
    raise FileNotFoundError(f"Нет GOST ключей в {KEY_PATH}")


def sign_xml(xml_string: str) -> str:
    """Подписывает XML строку через kalkan_sign C-wrapper."""
    key = find_key()
    print(f"  🔑 Используем ключ: {os.path.basename(key)}")
    result = subprocess.run(
        [SIGN_BIN, key, ECP_PASS, xml_string],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ошибка подписания: {result.stdout}\n{result.stderr}")
    signed = result.stdout.strip()
    if not signed or signed == "Success!":
        raise RuntimeError("C-wrapper не возвращает подписанный XML — нужно обновить kalkan_sign.c")
    return signed


def get_login_page(session: requests.Session) -> dict:
    """GET главной страницы — получаем ViewState, JSESSIONID и XML для подписи."""
    print("📡 GET index.xhtml ...")
    resp = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    xml_match = re.search(r'id="xmlToSign0"[^>]*value="([^"]+)"', html)
    if not xml_match:
        raise RuntimeError("Не найден xmlToSign0 на странице логина")
    xml_to_sign = html_lib.unescape(xml_match.group(1))
    print(f"  📄 XML для подписи получен")

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
    """Подписываем XML и отправляем AJAX-запрос для авторизации."""
    print("✍️  Подписываем XML через KalkanCrypt ...")
    signed_xml = sign_xml(page_data["xml_to_sign"])
    print(f"  ✅ Подписанный XML ({len(signed_xml)} байт)")

    payload = {
        page_data["eds_form"]: page_data["eds_form"],
        page_data["signed_field"]: signed_xml,
        "javax.faces.ViewState": page_data["view_state"],
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": page_data["ajax_btn_id"],
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        page_data["ajax_btn_id"]: page_data["ajax_btn_id"],
    }

    headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Faces-Request": "partial/ajax",
        "Accept": "application/xml, text/xml, */*; q=0.01",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/index.xhtml",
    }

    print("📡 RichFaces AJAX авторизация ...")
    resp = session.post(f"{BASE_URL}/index.xhtml", data=payload, headers=headers, timeout=30, allow_redirects=True)
    print(f"  HTTP {resp.status_code}, {len(resp.text)} байт")

    check = session.get(f"{BASE_URL}/index.xhtml", headers=HEADERS, timeout=30)
    if "Шығу" in check.text or "Выход" in check.text or "Сот кабинеті" in check.text:
        if "loginInfoForSign" not in check.text:
            print("  ✅ Авторизация успешна!")
            return True

    # Fallback — прямой POST
    print("  ⚠️  AJAX не дал сессию, пробуем прямой POST ...")
    payload2 = {
        page_data["eds_form"]: page_data["eds_form"],
        page_data["signed_field"]: signed_xml,
        "javax.faces.ViewState": page_data["view_state"],
    }
    resp2 = session.post(
        f"{BASE_URL}/index.xhtml",
        data=payload2,
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
        allow_redirects=True,
    )
    if "Шығу" in resp2.text or "Выход" in resp2.text:
        print("  ✅ Авторизация через прямой POST!")
        return True

    print("  ❌ Авторизация не удалась")
    with open("/output/auth_response.txt", "w") as f:
        f.write(f"AJAX resp ({resp.status_code}):\n{resp.text[:3000]}\n\nPOST resp ({resp2.status_code}):\n{resp2.text[:3000]}")
    return False


def solve_captcha(session: requests.Session) -> str:
    """Скачивает и решает капчу через ddddocr. Возвращает пустую строку при неудаче."""
    t = int(time.time() * 1000)
    resp = session.get(f"{BASE_URL}/img/captcha.jpg?t={t}", headers=HEADERS)
    content_type = resp.headers.get("Content-Type", "")
    if "image" not in content_type or len(resp.content) == 0:
        print(f"  ⚠️  Капча пустая ({len(resp.content)} байт) — шлём пустое поле")
        return ""
    try:
        ocr = ddddocr.DdddOcr(show_ad=False)
        result = ocr.classification(resp.content)
        print(f"  🤖 Капча: '{result}'")
        return result
    except Exception as e:
        print(f"  ⚠️  Ошибка OCR: {e}")
        return ""


def extract_view_state(html_or_xml: str) -> Optional[str]:
    """Извлекает актуальный ViewState из HTML или AJAX-XML."""
    m = re.search(r'id="j_id1:javax\.faces\.ViewState:\d+"[^>]*value="([^"]+)"', html_or_xml)
    if m:
        return m.group(1)
    m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html_or_xml)
    if m:
        return m.group(1)
    return None


def find_next_page_btn(soup: BeautifulSoup) -> Optional[str]:
    """Ищет кнопку ► (следующая страница) в RichFaces пагинаторе."""
    for tag in soup.find_all('a'):
        onclick = tag.get('onclick', '')
        txt = tag.get_text(strip=True)
        if 'thisPage' in onclick and txt in ['►', '>', '>>', '»', 'Следующая', '⇒']:
            return tag.get('id')
    return None


def get_next_page_num(soup: BeautifulSoup) -> Optional[int]:
    """Возвращает номер следующей страницы из onclick кнопки ►."""
    for tag in soup.find_all('a'):
        onclick = tag.get('onclick', '')
        txt = tag.get_text(strip=True)
        if 'thisPage' in onclick and txt in ['►', '>', '>>', '»', 'Следующая', '⇒']:
            m = re.search(r'"thisPage"\s*:\s*"(\d+)"', onclick)
            if m:
                return int(m.group(1))
    return None


def get_total_pages(soup: BeautifulSoup) -> int:
    """Определяет общее количество страниц — берём максимальный thisPage среди всех кнопок пагинации."""
    max_page = 1
    for tag in soup.find_all('a'):
        onclick = tag.get('onclick', '')
        if 'thisPage' in onclick:
            m = re.search(r'"thisPage"\s*:\s*"(\d+)"', onclick)
            if m:
                max_page = max(max_page, int(m.group(1)))
    return max_page


def navigate_to_next_page(session: requests.Session, view_state: str, list_form_id: str, next_btn_id: str, next_page_num: int) -> tuple[str, str]:
    """Кликает на следующую страницу через RichFaces AJAX. Возвращает (html, new_view_state)."""
    data = {
        list_form_id: list_form_id,
        "javax.faces.ViewState": view_state,
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": next_btn_id,
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        next_btn_id: next_btn_id,
        "thisPage": str(next_page_num),
    }
    resp = session.post(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=AJAX_HEADERS, data=data)
    new_vs = extract_view_state(resp.text) or view_state
    resp2 = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS)
    new_vs = extract_view_state(resp2.text) or new_vs
    return resp2.text, new_vs


def download_case_docs(session: requests.Session, param1: str, view_state: str, case_num: str) -> list[str]:
    """Открывает карточку дела, скачивает PDF/DOCX и возвращает список локальных путей."""
    downloaded = []
    ajax_h = {**AJAX_HEADERS, "Referer": f"{BASE_URL}/form/courtActs/lawsuitList.xhtml"}

    # Открываем карточку дела
    data_case = {
        "j_idt33:j_idt111": "j_idt33:j_idt111",
        "javax.faces.ViewState": view_state,
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt33:j_idt111:j_idt112",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        "j_idt33:j_idt111:j_idt112": "j_idt33:j_idt111:j_idt112",
        "param1": param1,
    }
    session.post(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=ajax_h, data=data_case)

    # Страница со списком документов
    for attempt in range(4):
        try:
            resp_docs = session.get(f"{BASE_URL}/form/courtActs/documentList.xhtml", headers=HEADERS)
            os.makedirs(PDF_DIR, exist_ok=True)
            html_path = os.path.join(PDF_DIR, f"{YEAR}_{case_num.replace('/', '_').replace(chr(92), '_')}_case.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(resp_docs.text)
            break
        except Exception as e:
            if attempt == 3:
                return []
            wait = 2 ** attempt
            time.sleep(wait)
            session.get(f"{BASE_URL}/", headers=HEADERS, timeout=10)
    doc_soup = BeautifulSoup(resp_docs.text, "html.parser")
    doc_vs_input = doc_soup.find("input", {"name": "javax.faces.ViewState"})
    doc_view_state = doc_vs_input.get("value") if doc_vs_input else view_state

    docs_found = doc_soup.find_all("a", {"onclick": lambda x: x and "downloadSelectedDoc" in x})

    for doc_a in docs_found:
        doc_name = doc_a.get_text(strip=True)
        doc_onclick = doc_a.get("onclick", "")
        doc_m = re.search(r"downloadSelectedDoc\('?([^',]+)'?,\s*'?([^',]+)'?\)", doc_onclick)
        if not doc_m:
            continue

        d_p1, d_p2 = doc_m.group(1), doc_m.group(2)
        print(f"    ⬇️  Скачиваем: {doc_name}")

        data_prep = {
            "j_idt33:j_idt36:j_idt61": "j_idt33:j_idt36:j_idt61",
            "javax.faces.ViewState": doc_view_state,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "j_idt33:j_idt36:j_idt61:j_idt62",
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "@all",
            "j_idt33:j_idt36:j_idt61:j_idt62": "j_idt33:j_idt36:j_idt61:j_idt62",
            "param1": d_p1,
            "param2": d_p2,
        }
        resp_prep = session.post(
            f"{BASE_URL}/form/courtActs/documentList.xhtml",
            headers={**ajax_h, "Referer": f"{BASE_URL}/form/courtActs/documentList.xhtml"},
            data=data_prep,
        )
        prep_vs = extract_view_state(resp_prep.text)
        if prep_vs:
            doc_view_state = prep_vs

        captcha_success = False
        for attempt_cap in range(5):
            captcha_val = solve_captcha(session)
            time.sleep(0.5)

            data_captcha = {
                "j_idt33:j_idt36:captchaForm": "j_idt33:j_idt36:captchaForm",
                "javax.faces.ViewState": doc_view_state,
                "j_idt33:j_idt36:captchaForm:edit-captcha": captcha_val,
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "j_idt33:j_idt36:captchaForm:downloadDocBtn",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "@all",
                "j_idt33:j_idt36:captchaForm:downloadDocBtn": "j_idt33:j_idt36:captchaForm:downloadDocBtn",
            }
            resp_cap = session.post(
                f"{BASE_URL}/form/courtActs/documentList.xhtml",
                headers={**ajax_h, "Referer": f"{BASE_URL}/form/courtActs/documentList.xhtml"},
                data=data_captcha,
            )

            n_m = re.search(r'name="n"[^>]*value="([^"]+)"', resp_cap.text)
            u_m = re.search(r'name="u"[^>]*value="([^"]+)"', resp_cap.text)

            if n_m and u_m:
                n_val = html_lib.unescape(n_m.group(1))
                u_val = html_lib.unescape(u_m.group(1))
                
                download_data = {"n": n_val, "u": u_val, "page": "/courtActs/documentList", "b64": "none", "inline": ""}
                resp_pdf = session.post(f"{BASE_URL}/ticket/fileDownload", data=download_data, headers=HEADERS)

                if resp_pdf.status_code == 200 and len(resp_pdf.content) > 0:
                    safe_name = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ_\-\.]", "_", doc_name)[:80]
                    magic = resp_pdf.content[:4]
                    if magic[:2] == b'PK': ext = ".docx"
                    elif magic == b'%PDF': ext = ".pdf"
                    else:
                        ct = resp_pdf.headers.get("Content-Type", "")
                        ext = ".docx" if "word" in ct or "docx" in ct else ".pdf"
                    
                    pdf_path = f"{PDF_DIR}/{YEAR}_{case_num.replace('/', '_').replace(chr(92), '_')}_{safe_name}{ext}"
                    with open(pdf_path, "wb") as f:
                        f.write(resp_pdf.content)
                    print(f"    💾 Сохранён: {os.path.basename(pdf_path)}")
                    downloaded.append(pdf_path)
                    captcha_success = True
                    break
            time.sleep(1)

        time.sleep(DOWNLOAD_DELAY)

    return downloaded


def search_and_download_all(session: requests.Session, cat_name: str, category_id: str):
    """Поиск + обход всех страниц + скачивание + Google Drive"""
    global tg_links_buffer
    print(f"\n🔍 Открываем Банк судебных актов (категория: {cat_name}, год: {YEAR}) ...")
    resp = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)

    view_state = extract_view_state(resp.text)
    if not view_state:
        print("❌ Не найден ViewState для поиска")
        return []

    print(f"📡 Поиск: {cat_name}, {YEAR} год ...")

    data_search = {
        "j_idt35:j_idt40:j_idt41": "j_idt35:j_idt40:j_idt41",
        "javax.faces.ViewState": view_state,
        "j_idt35:j_idt40:j_idt41:edit-category": category_id,
        "j_idt35:j_idt40:j_idt41:edit-period": YEAR,
        "j_idt35:j_idt40:j_idt41:edit-participantTypeCheckbox": "FIRSTINSTANCE",
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt35:j_idt40:j_idt41:j_idt138",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        "j_idt35:j_idt40:j_idt41:j_idt138": "j_idt35:j_idt40:j_idt41:j_idt138",
    }
    session.post(
        f"{BASE_URL}/form/courtActs/index.xhtml",
        headers={**AJAX_HEADERS, "Referer": f"{BASE_URL}/form/courtActs/index.xhtml"},
        data=data_search,
    )

    resp_list = session.get(f"{BASE_URL}/form/courtActs/lawsuitList.xhtml", headers=HEADERS)
    list_soup = BeautifulSoup(resp_list.text, "html.parser")
    view_state = extract_view_state(resp_list.text) or view_state

    total_pages = get_total_pages(list_soup)
    print(f"📊 Всего страниц: {total_pages}")

    list_form_id = "j_idt33:j_idt111"
    
    # ☁️ Создаем папку категории на Google Drive
    gdrive_cat_folder_id, gdrive_gdocs_cat_folder_id = get_or_create_gdrive_structure(cat_name)

    all_cases = []
    cat_file = f"/output/cases_{YEAR}_{category_id}.json"
    if os.path.exists(cat_file):
        with open(cat_file, "r", encoding="utf-8") as f:
            try:
                all_cases = json.load(f)
                print(f"  📂 Загружено {len(all_cases)} уже обработанных дел")
            except Exception:
                all_cases = []

    current_page = 1
    while True:
        print(f"\n{'='*50}")
        print(f"  📄 Страница {current_page}/{total_pages}")
        print(f"{'='*50}")

        rows = list_soup.find_all("tr", {"onclick": lambda x: x and "viewSelectedLawsuit" in x})
        print(f"  Дел на странице: {len(rows)}")

        for row in rows:
            cells = row.find_all(["td", "th"])
            clean_cells = [c.get_text(strip=True) for c in cells]
            case_num = clean_cells[0] if len(clean_cells) > 0 else "unknown"

            if any("Медиация" in c for c in clean_cells):
                continue

            onclick = row.get("onclick", "")
            m = re.search(r"viewSelectedLawsuit\('([^']+)'\)", onclick)
            param1 = m.group(1) if m else str(rows.index(row))

            unique_key = f"{current_page}:{param1}"
            already_done = any(c.get("unique_key") == unique_key for c in all_cases)
            if already_done:
                print(f"  ⏭️  Пропускаем (уже скачано): {unique_key}")
                continue

            print(f"\n  📁 Дело {param1}: {' | '.join(clean_cells[:3])}")

            docs = []
            for retry in range(3):
                try:
                    docs = download_case_docs(session, param1, view_state, case_num)
                    break
                except Exception as e:
                    wait = 3 * (retry + 1)
                    time.sleep(wait)

            # Загрузка на Google Drive и логирование
            gdrive_links = []
            if gdrive_cat_folder_id:
                for doc_path in docs:
                    print(f"    ☁️ Загрузка оригинала на Google Drive: {os.path.basename(doc_path)}")
                    upload_resp = upload_file_to_drive(doc_path, gdrive_cat_folder_id)
                    
                    if gdrive_gdocs_cat_folder_id:
                        print(f"    ☁️ Конвертация в Google Docs: {os.path.basename(doc_path)}")
                        upload_file_to_drive(doc_path, gdrive_gdocs_cat_folder_id, as_gdoc=True)

                    if upload_resp and "webViewLink" in upload_resp:
                        link = upload_resp["webViewLink"]
                        gdrive_links.append(link)
                        log_to_csv(case_num, cat_name, doc_path, link)
                        print(f"    ✅ Загружено в GDrive: {link}")
                    else:
                        log_to_csv(case_num, cat_name, doc_path, "Ошибка загрузки")
            else:
                for doc_path in docs:
                    log_to_csv(case_num, cat_name, doc_path, "GDrive отключен")

            case_data = {
                "unique_key": unique_key,
                "param1": param1,
                "data": clean_cells,
                "docs": docs,
                "gdrive_links": gdrive_links,
                "page": current_page,
                "parsed_at": datetime.now().isoformat(),
            }
            all_cases.append(case_data)

            with open(cat_file, "w", encoding="utf-8") as f:
                json.dump(all_cases, f, ensure_ascii=False, indent=2)
            
            # Добавляем в буфер ТГ
            if gdrive_links:
                tg_links_buffer.append(f"📄 {case_num}: {gdrive_links[0]}")
            else:
                tg_links_buffer.append(f"📄 {case_num}: Скачано на диск (нет GDrive)")
            
            # Отправляем в ТГ каждые 10 дел
            if len(tg_links_buffer) >= 10:
                text = f"📂 Категория: {cat_name}\nНовые скачанные дела (10 шт):\n\n" + "\n".join(tg_links_buffer)
                send_tg_message(text)
                tg_links_buffer.clear()

        if current_page >= total_pages:
            print(f"\n✅ Все {total_pages} страниц обработаны!")
            if len(tg_links_buffer) > 0:
                text = f"📂 Категория: {cat_name}\nПоследние дела ({len(tg_links_buffer)} шт):\n\n" + "\n".join(tg_links_buffer)
                send_tg_message(text)
                tg_links_buffer.clear()
            break

        next_btn_id = find_next_page_btn(list_soup)
        next_page_num = get_next_page_num(list_soup)

        if not next_btn_id or not next_page_num:
            break

        next_target = current_page + 1
        try:
            new_html, view_state = navigate_to_next_page(session, view_state, list_form_id, next_btn_id, next_target)
        except Exception as e:
            time.sleep(5)
            page_data = get_login_page(session)
            if page_data:
                login_with_eds(session, page_data)
            new_html, view_state = navigate_to_next_page(session, view_state, list_form_id, next_btn_id, next_target)

        list_soup = BeautifulSoup(new_html, "html.parser")
        current_page += 1
        new_total = get_total_pages(list_soup)
        if new_total:
            total_pages = new_total

        time.sleep(1)

    return all_cases


def main():
    print("==================================================")
    print("  ПАРСЕР СУДЕБНЫХ ДЕЛ — office.sud.kz (ТК РК)")
    print(f"  Год: {YEAR}")
    print("==================================================")

    if not MATON_API_KEY:
        print("⚠️ MATON_API_KEY не установлен! Загрузка в Google Drive будет пропущена.")

    max_restarts = 5
    for attempt in range(max_restarts):
        try:
            session = requests.Session()
            session.verify = False
            requests.packages.urllib3.disable_warnings()

            page_data = get_login_page(session)
            if not page_data:
                print("Не удалось получить страницу логина.")
                time.sleep(5)
                continue

            if login_with_eds(session, page_data):
                send_tg_message(f"🚀 Запуск парсера на VPS. Год: {YEAR}\nБэкап в Google Drive: {'✅ Да' if MATON_API_KEY else '❌ Нет'}")
                categories = {
                    "Трудовые споры": "142030000100000000",
                    "Договор подряда": "142030001200070000",
                    "Взыскание долга": "142010000600000000"
                }
                for c_name, c_id in categories.items():
                    try:
                        search_and_download_all(session, c_name, c_id)
                    except Exception as e:
                        print(f"❌ Ошибка парсинга {c_name}: {e}")
                
                if len(tg_links_buffer) > 0:
                    send_tg_message("Остаток ссылок:\n" + "\n".join(tg_links_buffer))
                    tg_links_buffer.clear()
                    
                print(f"\n✅ Готово! Скрипт завершил работу без критических сбоев.")
                send_tg_message(f"🏁 Парсинг всех категорий за {YEAR} завершен!")
                break
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            print(f"🔄 Перезапуск всего парсера через 10 секунд (попытка {attempt+1}/{max_restarts})...")
            time.sleep(10)

if __name__ == "__main__":
    main()
