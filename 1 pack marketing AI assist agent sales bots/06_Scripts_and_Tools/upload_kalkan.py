import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env')
MATON_API_KEY = os.getenv('MATON_API_KEY')

def get_or_create_folder(folder_name):
    print(f"Ищем папку '{folder_name}' на Google Drive...")
    url = "https://gateway.maton.ai/google-drive/drive/v3/files"
    params = {
        "q": f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
        "fields": "files(id, name)"
    }
    headers = {"Authorization": f"Bearer {MATON_API_KEY}"}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        files = resp.json().get('files', [])
        if files:
            print(f"Папка найдена: {files[0]['id']}")
            return files[0]['id']
            
    print("Папка не найдена, создаем...")
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    resp = requests.post(url, headers=headers, json=metadata)
    if resp.status_code == 200:
        folder_id = resp.json().get('id')
        print(f"Создана папка: {folder_id}")
        return folder_id
    else:
        print(f"Ошибка создания папки: {resp.text}")
        return None

def upload_zip(file_path, folder_id):
    filename = os.path.basename(file_path)
    print(f"Начинаю загрузку {filename} (размер: {os.path.getsize(file_path)/1024/1024:.1f} МБ)...")
    url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart"
    metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    
    with open(file_path, "rb") as f:
        files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (filename, f, "application/zip")
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}"}, files=files)
        
    if resp.status_code == 200:
        file_id = resp.json().get("id")
        link = f"https://drive.google.com/file/d/{file_id}/view"
        print(f"Файл успешно загружен! Устанавливаем права доступа...")
        
        # Делаем публичным
        share_url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{file_id}/permissions"
        requests.post(share_url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"},
                      json={"role": "reader", "type": "anyone"})
        return link
    else:
        print(f"Ошибка загрузки: {resp.text}")
        return None

if __name__ == "__main__":
    file_path = "kalkan_docker.zip"
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден!")
    else:
        folder_id = get_or_create_folder("Backups")
        if folder_id:
            link = upload_zip(file_path, folder_id)
            if link:
                print(f"✅ ФАЙЛ ЗАГРУЖЕН НА GOOGLE DRIVE: {link}")
