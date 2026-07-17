#!/usr/bin/env python3
"""
Конвертирует docx файлы в Google Documents на Google Драйве через Maton API.
Также перемещает HTML файлы в подпапку.

Usage:
    python convert_docx_to_gdocs.py --folder-id FOLDER_ID
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests

BASE_URL = "https://gateway.maton.ai/google-drive"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

# Будет подтянут из .env
def load_env() -> Dict[str, str]:
    """Загружает переменные окружения из .env файлов."""
    env: Dict[str, str] = dict(os.environ)
    script_path = Path(__file__).resolve()
    project_root = Path(__file__).resolve().parents[1]

    # Ищем .env в AI_Lawyer и во всех родительских папках, потому что ключ Maton
    # в этом workspace лежит выше текущего проекта.
    env_paths = [project_root / ".env"] + [parent / ".env" for parent in script_path.parents]
    seen_paths = set()
    for env_path in env_paths:
        if env_path in seen_paths:
            continue
        seen_paths.add(env_path)
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


def get_folder_files(folder_id: str, mime_type_filter: Optional[str] = None) -> List[Dict]:
    """Получает список файлов в папке с опциональной фильтрацией по MIME типу."""
    query = f"'{folder_id}' in parents and trashed = false"
    if mime_type_filter:
        query += f" and mimeType = '{mime_type_filter}'"
    
    resp = requests.get(
        f"{BASE_URL}/drive/v3/files",
        headers=HEADERS_AUTH,
        params={"q": query, "fields": "files(id, name, mimeType)", "pageSize": 1000},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("files", [])


def find_or_create_folder(name: str, parent_id: Optional[str] = None) -> str:
    """Находит или создаёт папку."""
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    resp = requests.get(
        f"{BASE_URL}/drive/v3/files",
        headers=HEADERS_AUTH,
        params={"q": query, "fields": "files(id, name)"},
        timeout=60,
    )
    resp.raise_for_status()
    files = resp.json().get("files", [])
    
    if files:
        return files[0]["id"]
    
    # Создаём папку
    data = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        data["parents"] = [parent_id]
    
    resp = requests.post(f"{BASE_URL}/drive/v3/files", headers=HEADERS_JSON, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()["id"]


def copy_file_to_google_doc(file_id: str, file_name: str) -> str:
    """
    Конвертирует файл в Google Document.
    Для docx используем mimeType application/vnd.google-apps.document при копировании.
    """
    # Получаем metadata файла
    meta_resp = requests.get(
        f"{BASE_URL}/drive/v3/files/{file_id}",
        headers=HEADERS_AUTH,
        params={"fields": "id, name, parents"},
        timeout=60,
    )
    meta_resp.raise_for_status()
    metadata = meta_resp.json()
    
    # Создаём копию с конвертацией
    # Для docx: указываем mimeType Google Docs
    copy_metadata = {
        "name": file_name.replace(".docx", ""),
        "mimeType": "application/vnd.google-apps.document"
    }
    if metadata.get("parents"):
        copy_metadata["parents"] = metadata["parents"]
    
    resp = requests.post(
        f"{BASE_URL}/drive/v3/files/{file_id}/copy",
        headers=HEADERS_JSON,
        json=copy_metadata,
        timeout=120,
    )
    
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Copy failed for {file_name}: {resp.status_code} {resp.text}")
    
    return resp.json()["id"]


def move_file_to_folder(file_id: str, folder_id: str) -> None:
    """Перемещает файл в указанную папку."""
    # Получаем текущие родители
    file_resp = requests.get(
        f"{BASE_URL}/drive/v3/files/{file_id}",
        headers=HEADERS_AUTH,
        params={"fields": "parents"},
        timeout=60,
    )
    file_resp.raise_for_status()
    current_parents = file_resp.json().get("parents", [])
    
    # Перемещаем (удаляем старых родителей, добавляем нового)
    resp = requests.patch(
        f"{BASE_URL}/drive/v3/files/{file_id}",
        headers=HEADERS_JSON,
        params={"addParents": folder_id, "removeParents": ",".join(current_parents)},
        json={},
        timeout=60,
    )
    resp.raise_for_status()


def run(folder_id: str, html_subfolder_name: str = "html") -> None:
    """
    Основная логика:
    1. Находит все docx файлы в папке
    2. Конвертирует их в Google Docs
    3. Перемещает HTML файлы в подпапку
    """
    print(f"📂 Работаю с папкой: {folder_id}")
    
    # Получаем информацию о папке
    folder_resp = requests.get(
        f"{BASE_URL}/drive/v3/files/{folder_id}",
        headers=HEADERS_AUTH,
        params={"fields": "name"},
        timeout=60,
    )
    folder_resp.raise_for_status()
    folder_name = folder_resp.json().get("name", "Unknown")
    print(f"📁 Папка: {folder_name}")
    
    # Находим все файлы
    all_files = get_folder_files(folder_id)
    docx_files = [f for f in all_files if f["mimeType"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    html_files = [f for f in all_files if f["mimeType"] == "text/html" or f["name"].endswith(".html")]
    
    print(f"\n📊 Найдено:")
    print(f"   DOCX: {len(docx_files)}")
    print(f"   HTML: {len(html_files)}")
    
    # Создаём подпапку для HTML
    html_folder_id = find_or_create_folder(html_subfolder_name, folder_id)
    print(f"\n📁 Подпапка для HTML создана: {html_subfolder_name}")
    
    # Конвертируем docx → Google Docs
    converted = []
    for docx in docx_files:
        try:
            print(f"\n🔄 Конвертирую: {docx['name']}")
            doc_id = copy_file_to_google_doc(docx["id"], docx["name"])
            converted.append({"original": docx["name"], "google_doc_id": doc_id})
            print(f"   ✅ Создан Google Doc: https://docs.google.com/document/d/{doc_id}/edit")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    # Перемещаем HTML файлы в подпапку
    moved_html = []
    for html in html_files:
        try:
            print(f"\n📄 Перемещаю HTML: {html['name']}")
            move_file_to_folder(html["id"], html_folder_id)
            moved_html.append(html["name"])
            print(f"   ✅ Перемещён в подпапку")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    # Сохраняем результат
    result = {
        "folder_id": folder_id,
        "folder_name": folder_name,
        "converted_docx": converted,
        "moved_html": moved_html,
    }
    
    output_path = Path(__file__).parent.parent / "data" / "conversion_results.json"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n📊 Итог:")
    print(f"   Конвертировано docx → Google Docs: {len(converted)}")
    print(f"   Перемещено HTML файлов: {len(moved_html)}")
    print(f"💾 Результат: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Конвертация docx в Google Docs через Maton API")
    parser.add_argument("--folder-id", required=True, help="ID папки на Google Драйве")
    parser.add_argument("--html-folder", default="html", help="Название подпапки для HTML файлов")
    args = parser.parse_args()
    run(args.folder_id, args.html_folder)