#!/usr/bin/env python3
"""
Пакетно продолжает подготовку Google Drive папки для NotebookLM:
- перемещает HTML файлы из корня в подпапку html;
- конвертирует DOCX в Google Docs;
- пропускает DOCX, если Google Doc с таким же именем уже существует.

Сделано пакетами, чтобы команда не упиралась в timeout Cline.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests

BASE_URL = "https://gateway.maton.ai/google-drive"
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
HTML_MIME = "text/html"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


def load_env() -> Dict[str, str]:
    """Загружает переменные окружения из окружения и .env в родительских папках."""
    env: Dict[str, str] = dict(os.environ)
    script_path = Path(__file__).resolve()
    for env_path in [parent / ".env" for parent in script_path.parents]:
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
    raise SystemExit("MATON_API_KEY не найден")

HEADERS_JSON = {"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"}
HEADERS_AUTH = {"Authorization": f"Bearer {MATON_API_KEY}"}


def api_get(path: str, **kwargs) -> requests.Response:
    kwargs.setdefault("timeout", 60)
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS_AUTH, **kwargs)
    resp.raise_for_status()
    return resp


def api_post(path: str, json_body: Dict, timeout: int = 90) -> requests.Response:
    resp = requests.post(f"{BASE_URL}{path}", headers=HEADERS_JSON, json=json_body, timeout=timeout)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"POST {path} failed: {resp.status_code} {resp.text}")
    return resp


def api_patch(path: str, params: Dict, json_body: Dict) -> requests.Response:
    resp = requests.patch(f"{BASE_URL}{path}", headers=HEADERS_JSON, params=params, json=json_body, timeout=60)
    resp.raise_for_status()
    return resp


def list_children(folder_id: str) -> List[Dict]:
    """Возвращает файлы, лежащие прямо в папке."""
    resp = api_get(
        "/drive/v3/files",
        params={
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "files(id, name, mimeType, parents)",
            "pageSize": 1000,
        },
    )
    return resp.json().get("files", [])


def get_folder_name(folder_id: str) -> str:
    resp = api_get(f"/drive/v3/files/{folder_id}", params={"fields": "name"})
    return resp.json().get("name", "Unknown")


def find_or_create_folder(name: str, parent_id: str) -> str:
    children = list_children(parent_id)
    for item in children:
        if item.get("name") == name and item.get("mimeType") == GOOGLE_FOLDER_MIME:
            return item["id"]
    metadata = {"name": name, "mimeType": GOOGLE_FOLDER_MIME, "parents": [parent_id]}
    return api_post("/drive/v3/files", metadata, timeout=60).json()["id"]


def doc_name_from_docx(file_name: str) -> str:
    return file_name[:-5] if file_name.lower().endswith(".docx") else file_name


def move_file_to_folder(file_id: str, target_folder_id: str, current_parents: Optional[List[str]]) -> None:
    if current_parents is None:
        current_parents = api_get(f"/drive/v3/files/{file_id}", params={"fields": "parents"}).json().get("parents", [])
    api_patch(
        f"/drive/v3/files/{file_id}",
        params={"addParents": target_folder_id, "removeParents": ",".join(current_parents)},
        json_body={},
    )


def copy_docx_as_google_doc(file_id: str, target_name: str, parent_id: str) -> str:
    metadata = {"name": target_name, "mimeType": GOOGLE_DOC_MIME, "parents": [parent_id]}
    return api_post(f"/drive/v3/files/{file_id}/copy", metadata, timeout=120).json()["id"]


def save_state(state: Dict) -> None:
    out = Path(__file__).resolve().parents[1] / "data" / "batch_conversion_state.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run(folder_id: str, html_folder_name: str, html_limit: int, docx_limit: int) -> None:
    folder_name = get_folder_name(folder_id)
    html_folder_id = find_or_create_folder(html_folder_name, folder_id)
    children = list_children(folder_id)

    html_files = [f for f in children if f.get("mimeType") == HTML_MIME or f.get("name", "").lower().endswith(".html")]
    docx_files = [f for f in children if f.get("mimeType") == DOCX_MIME]
    google_docs_by_name = {f["name"]: f for f in children if f.get("mimeType") == GOOGLE_DOC_MIME}

    state = {
        "folder_id": folder_id,
        "folder_name": folder_name,
        "html_folder_id": html_folder_id,
        "root_html_total_before_batch": len(html_files),
        "root_docx_total": len(docx_files),
        "google_docs_total_before_batch": len(google_docs_by_name),
        "moved_html": [],
        "converted_docx": [],
        "skipped_docx": [],
        "errors": [],
    }

    print(f"📁 Папка: {folder_name}")
    print(f"📊 В корне сейчас: DOCX={len(docx_files)}, HTML={len(html_files)}, Google Docs={len(google_docs_by_name)}")

    for index, html in enumerate(html_files[:html_limit], start=1):
        try:
            print(f"📄 HTML [{index}/{min(html_limit, len(html_files))}]: {html['name']}")
            move_file_to_folder(html["id"], html_folder_id, html.get("parents"))
            state["moved_html"].append({"name": html["name"], "file_id": html["id"]})
            save_state(state)
            print("   ✅ перемещён")
        except Exception as exc:
            msg = f"HTML move failed for {html['name']}: {exc}"
            state["errors"].append(msg)
            save_state(state)
            print(f"   ❌ {exc}")

    converted_count = 0
    for docx in docx_files:
        target_name = doc_name_from_docx(docx["name"])
        if target_name in google_docs_by_name:
            state["skipped_docx"].append({"original": docx["name"], "google_doc_id": google_docs_by_name[target_name]["id"]})
            continue
        if converted_count >= docx_limit:
            break
        try:
            converted_count += 1
            print(f"🔄 DOCX [{converted_count}/{docx_limit}]: {docx['name']}")
            doc_id = copy_docx_as_google_doc(docx["id"], target_name, folder_id)
            google_docs_by_name[target_name] = {"id": doc_id, "name": target_name, "mimeType": GOOGLE_DOC_MIME}
            state["converted_docx"].append({"original": docx["name"], "google_doc_id": doc_id})
            save_state(state)
            print(f"   ✅ https://docs.google.com/document/d/{doc_id}/edit")
        except Exception as exc:
            msg = f"DOCX convert failed for {docx['name']}: {exc}"
            state["errors"].append(msg)
            save_state(state)
            print(f"   ❌ {exc}")

    children_after = list_children(folder_id)
    html_after = [f for f in children_after if f.get("mimeType") == HTML_MIME or f.get("name", "").lower().endswith(".html")]
    docs_after = [f for f in children_after if f.get("mimeType") == GOOGLE_DOC_MIME]
    state["root_html_total_after_batch"] = len(html_after)
    state["google_docs_total_after_batch"] = len(docs_after)
    save_state(state)

    print("\n📊 Итог батча:")
    print(f"   HTML перемещено: {len(state['moved_html'])}; осталось HTML в корне: {len(html_after)}")
    print(f"   DOCX сконвертировано в батче: {len(state['converted_docx'])}")
    print(f"   DOCX пропущено, потому что Google Doc уже есть: {len(state['skipped_docx'])}")
    print(f"   Google Docs в корне теперь: {len(docs_after)}")
    print(f"   Ошибок: {len(state['errors'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Пакетная конвертация DOCX и перенос HTML на Google Drive")
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--html-folder", default="html")
    parser.add_argument("--html-limit", type=int, default=20)
    parser.add_argument("--docx-limit", type=int, default=5)
    args = parser.parse_args()
    run(args.folder_id, args.html_folder, args.html_limit, args.docx_limit)
