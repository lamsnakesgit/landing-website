import os
import glob
import json
import requests
from dotenv import load_dotenv

# Load env variables
load_dotenv('.env')
MATON_API_KEY = os.getenv('MATON_API_KEY')
BOT_TOKEN = '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g'
CHAT_ID = '888005446'

def send_tg_message(text):
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        json={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    )

def get_or_create_folder(folder_name):
    print(f"Ищем папку '{folder_name}'...")
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
    resp = requests.post(
        url,
        headers=headers,
        json=metadata
    )
    if resp.status_code == 200:
        folder_id = resp.json().get('id')
        print(f"Создана папка: {folder_id}")
        return folder_id
    else:
        print(f"Ошибка создания папки: {resp.text}")
        return None

def upload_file(file_path, folder_id):
    filename = os.path.basename(file_path)
    print(f"Загружаем {filename}...")
    url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart"
    metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    
    with open(file_path, "rb") as f:
        files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (filename, f, "application/pdf")
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {MATON_API_KEY}"}, files=files)
        
    if resp.status_code == 200:
        file_id = resp.json().get("id")
        link = f"https://drive.google.com/file/d/{file_id}/view"
        
        # Делаем публичным для чтения
        share_url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{file_id}/permissions"
        requests.post(share_url, headers={"Authorization": f"Bearer {MATON_API_KEY}", "Content-Type": "application/json"},
                      json={"role": "reader", "type": "anyone"})
                      
        return link
    else:
        print(f"Ошибка загрузки {filename}: {resp.text}")
        return None

def main():
    if not MATON_API_KEY:
        print("MATON_API_KEY не найден в .env")
        return
        
    pdf_dir = "output/pdfs"
    pdfs = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdfs:
        print("PDF файлы не найдены.")
        return
        
    folder_id = get_or_create_folder("ии_юрист")
    if not folder_id:
        return
        
    send_tg_message(f"🔄 Начинаю загрузку {len(pdfs)} PDF в Google Drive (папка 'ии_юрист') через Maton AI...")
    
    links = []
    for pdf in pdfs:
        link = upload_file(pdf, folder_id)
        if link:
            links.append(f"📄 {os.path.basename(pdf)}: \n{link}")
            
        # Отправляем пачками по 10 штук чтобы не спамить
        if len(links) >= 10:
            msg = "📂 <b>Новые дела загружены:</b>\n\n" + "\n\n".join(links)
            send_tg_message(msg)
            links = []
            
    if links:
        msg = "📂 <b>Остальные дела загружены:</b>\n\n" + "\n\n".join(links)
        send_tg_message(msg)
        
    send_tg_message("✅ Все текущие скачанные файлы успешно загружены в Google Drive!")

if __name__ == "__main__":
    main()
