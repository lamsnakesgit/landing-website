#!/usr/bin/env python3
"""
Архивирует результаты src/sud_parser.py (court-acts режим) на Google Drive
через gateway.maton.ai: папки по году/месяцу дела + Google Doc на каждое дело
с ссылкой на источник и ссылкой на скриншот страницы результатов (для проверки).

Не делает файлы публичными: дела содержат ФИО сторон, архив остаётся приватным
для аккаунта, подключённого к Maton.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = PROJECT_ROOT.parents[1]  # "1 pack marketing AI assist agent sales bots"
OUTPUT_DIR = PROJECT_ROOT / "data" / "court_acts"

BASE_URL = "https://gateway.maton.ai/google-drive"


def load_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    for env_path in (PACK_ROOT / ".env", PROJECT_ROOT / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            env.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    return env


ENV = load_env()
MATON_API_KEY = ENV.get("MATON_API_KEY") or ENV.get("MOTON_API_KEY")
if not MATON_API_KEY:
    raise SystemExit("MATON_API_KEY не найден ни в AI_Lawyer/.env, ни в корневом .env")

HEADERS_JSON = {"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}
HEADERS_AUTH = {"Authorization": f"Bearer {MATON_API_KEY}"}


def find_folder(name: str, parent_id: Optional[str]) -> Optional[str]:
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    resp = requests.get(
        f"{BASE_URL}/drive/v3/files",
        headers=HEADERS_AUTH,
        params={"q": query, "fields": "files(id, name)"},
    )
    resp.raise_for_status()
    files = resp.json().get("files", [])
    return files[0]["id"] if files else None


def create_folder(name: str, parent_id: Optional[str] = None) -> str:
    data = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        data["parents"] = [parent_id]
    resp = requests.post(f"{BASE_URL}/drive/v3/files", headers=HEADERS_JSON, json=data)
    resp.raise_for_status()
    return resp.json()["id"]


def get_or_create_folder(name: str, parent_id: Optional[str] = None) -> str:
    existing = find_folder(name, parent_id)
    if existing:
        return existing
    return create_folder(name, parent_id)


def upload_bytes(name: str, content: bytes, mime_type: str, folder_id: Optional[str], convert_mime: Optional[str] = None) -> str:
    metadata = {"name": name, "mimeType": convert_mime or mime_type}
    if folder_id:
        metadata["parents"] = [folder_id]

    resp = requests.post(
        f"{BASE_URL}/upload/drive/v3/files?uploadType=multipart",
        headers=HEADERS_AUTH,
        files={
            "metadata": (None, json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": (name, content, mime_type),
        },
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed for {name}: {resp.status_code} {resp.text}")
    return resp.json()["id"]


def drive_link(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"


def parse_case_date(date_str: str) -> Optional[datetime]:
    for fmt in ("%d.%m.%Y",):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def safe_filename(value: str, max_len: int = 80) -> str:
    value = re.sub(r"[^0-9A-Za-zА-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүІіҺһ_.\\- ]+", "_", value or "").strip()
    return (value or "case")[:max_len]


def build_case_doc_html(case: Dict, verification_link: str) -> str:
    links_html = "".join(f'<li><a href="{link}">{link}</a></li>' for link in case.get("links", []))
    return f"""<html><body>
<h2>Дело №{case.get('case_number') or '(не определён)'}</h2>
<p><b>Суд:</b> {case.get('court') or '-'}</p>
<p><b>Категория:</b> {case.get('category') or '-'}</p>
<p><b>Стороны:</b> {case.get('parties') or '-'}</p>
<p><b>Судья:</b> {case.get('judge') or '-'}</p>
<p><b>Результат:</b> {case.get('result') or '-'}</p>
<p><b>Дата:</b> {case.get('date') or '-'}</p>
<hr>
<p><b>Текст строки результата (raw):</b></p>
<p>{case.get('text') or ''}</p>
<hr>
<p><b>Ссылки на источник (office.sud.kz):</b></p>
<ul>{links_html or '<li>нет ссылок</li>'}</ul>
<hr>
<p><b>Скриншот страницы результатов поиска (проверка, что агент спарсил корректно):</b><br>
<a href="{verification_link}">{verification_link}</a></p>
</body></html>"""


def run(results_path: Path, root_folder_name: str) -> None:
    if not results_path.exists():
        raise SystemExit(f"Файл результатов не найден: {results_path}")

    results: List[Dict] = json.loads(results_path.read_text(encoding="utf-8"))
    if not results:
        print("⚠️  court_acts_results.json пуст (0 дел) — нечего архивировать.")
        print("    Скорее всего reCAPTCHA не была пройдена вручную в последнем запуске парсера.")
        return

    print(f"📁 Корневая папка: {root_folder_name}")
    root_id = get_or_create_folder(root_folder_name)

    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M")
    verification_root = get_or_create_folder("_verification", root_id)
    verification_folder = create_folder(run_id, verification_root)

    verification_link = f"https://drive.google.com/drive/folders/{verification_folder}"
    html_snapshot = OUTPUT_DIR / "court_acts_search_results.html"
    png_snapshot = OUTPUT_DIR / "court_acts_search_results.png"

    if html_snapshot.exists():
        upload_bytes(
            "court_acts_search_results.html",
            html_snapshot.read_bytes(),
            "text/html",
            verification_folder,
        )
    if png_snapshot.exists():
        png_id = upload_bytes(
            "court_acts_search_results.png",
            png_snapshot.read_bytes(),
            "image/png",
            verification_folder,
        )
        verification_link = drive_link(png_id)

    print(f"🔍 Скриншот/HTML проверки загружены: {verification_link}")

    uploaded = []
    for case in results:
        case_date = parse_case_date(case.get("date", ""))
        year = str(case_date.year) if case_date else "без_даты"
        month = f"{case_date.month:02d}" if case_date else "00"

        year_folder = get_or_create_folder(year, root_id)
        month_folder = get_or_create_folder(month, year_folder)

        doc_name = safe_filename(f"{case.get('case_number') or case.get('row_index')} {case.get('parties') or ''}")
        doc_html = build_case_doc_html(case, verification_link)

        doc_id = upload_bytes(
            f"{doc_name}.html",
            doc_html.encode("utf-8"),
            "text/html",
            month_folder,
            convert_mime="application/vnd.google-apps.document",
        )
        link = drive_link(doc_id)
        uploaded.append({"case_number": case.get("case_number"), "doc_id": doc_id, "doc_link": link, "folder": f"{year}/{month}"})
        print(f"✅ {year}/{month}: {doc_name} → {link}")

    summary_path = OUTPUT_DIR / "drive_export_results.json"
    summary_path.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📊 Загружено дел: {len(uploaded)}")
    print(f"📁 Корень архива: https://drive.google.com/drive/folders/{root_id}")
    print(f"💾 Сводка: {summary_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Экспорт распарсенных дел ТК РК на Google Drive через Maton")
    parser.add_argument("--results", default=str(OUTPUT_DIR / "court_acts_results.json"))
    parser.add_argument("--root-folder", default="ТК РК - Трудовые споры (архив)")
    args = parser.parse_args()
    run(Path(args.results), args.root_folder)
