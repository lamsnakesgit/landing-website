#!/usr/bin/env python3
"""
Скрипт загрузки файлов на Google Drive через maton.ai API Gateway.
Использует MATON_API_KEY из .env
"""

import os
import sys
import json
import requests
from pathlib import Path

# Загрузка .env
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key, val)

load_env()

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("❌ MATON_API_KEY не найден в .env")
    sys.exit(1)

BASE_URL = "https://gateway.maton.ai/google-drive"
CTRL_URL = "https://ctrl.maton.ai"


def create_folder(name, parent_id=None):
    """Создание папки на Google Drive"""
    url = f"{BASE_URL}/drive/v3/files"
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
        json=data
    )
    return resp.json()


def upload_file(file_path, folder_id=None):
    """Загрузка файла через multipart upload"""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        return None

    url = f"{BASE_URL}/upload/drive/v3/files?uploadType=multipart"

    metadata = {"name": file_path.name}
    if folder_id:
        metadata["parents"] = [folder_id]

    # Определяем MIME тип
    ext = file_path.suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }
    mime_type = mime_types.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        files = {
            "metadata": (None, json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": (file_path.name, f, mime_type)
        }
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {MATON_API_KEY}"},
            files=files
        )

    if resp.status_code in (200, 201):
        result = resp.json()
        print(f"✅ Загружено: {file_path.name} → ID: {result.get('id')}")
        return result
    else:
        print(f"❌ Ошибка загрузки {file_path.name}: {resp.status_code} {resp.text}")
        return None


def make_public(file_id):
    """Открыть доступ к файлу для всех по ссылке"""
    url = f"{BASE_URL}/drive/v3/files/{file_id}/permissions"
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
        json=data
    )
    return resp.status_code in (200, 201)


def get_share_link(file_id):
    """Получить shareable ссылку"""
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"


def main():
    # Файлы для загрузки (юридическая тематика)
    files_to_upload = [
        "2 1 контент план_/ilovepdf_converted/Vnesudebnoe-bankrotstvo-v-Kazahstane.pdf",
        "2 1 контент план_/ilovepdf_converted/Bankrotstvo-fizicheskih-lic.pdf",
        "2 1 контент план_/26 12 25 - охват /Долг_Пять_Шагов_До_Банкротства.pdf",
        "2 1 контент план_/26 12 25 - охват /Упрощённый_режим_2026_Кто_исключён карусель номера.pdf",
        "2 1 контент план_/26 12 25 - охват /УПРОЩЁННЫЙ_РЕЖИМ_2026_ИСКЛЮЧЕНИЯ_И_РИСКИ 4 5 горизональо.pdf",
        "2 1 контент план_/26 12 25 - охват /УСН_2026_Обязательный_переход 2я карусель.pdf",
        "2 1 контент план_/26 12 25 - охват /УСН_2026_Ограничения карусель 7-8 1 .pdf",
    ]

    base_dir = Path(__file__).parent.parent

    # Создаём папку "ИИ Юрист"
    print("📁 Создаём папку 'ИИ Юрист'...")
    folder = create_folder("ИИ Юрист")
    folder_id = folder.get("id")
    print(f"✅ Папка создана: ID={folder_id}")

    results = []
    for rel_path in files_to_upload:
        full_path = base_dir / rel_path
        result = upload_file(full_path, folder_id)
        if result:
            file_id = result.get("id")
            make_public(file_id)
            link = get_share_link(file_id)
            results.append({
                "name": result.get("name"),
                "id": file_id,
                "link": link
            })
            print(f"🔗 Ссылка: {link}")

    # Сохраняем результаты
    output = {
        "folder_id": folder_id,
        "folder_link": f"https://drive.google.com/drive/folders/{folder_id}",
        "files": results
    }
    output_path = base_dir / "drive_upload_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Загружено {len(results)} файлов")
    print(f"📁 Папка: {output['folder_link']}")
    print(f"💾 Результаты сохранены в: {output_path}")

    return output


if __name__ == "__main__":
    main()