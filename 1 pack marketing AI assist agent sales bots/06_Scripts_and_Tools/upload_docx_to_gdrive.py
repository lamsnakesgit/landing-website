import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Путь к сервисному аккаунту
SERVICE_ACCOUNT_FILE = 'vertex_sa.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_to_docs():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': 'Судебные Логи (AI Lawyer)',
        'mimeType': 'application/vnd.google-apps.document' # Конвертируем в Google Doc
    }
    
    media = MediaFileUpload('output/Parsing_Logs_Word.docx',
                            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            resumable=True)
                            
    print("Загрузка файла в Google Drive...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    
    file_id = file.get('id')
    print(f"Файл загружен. ID: {file_id}")
    
    # Открываем доступ для всех, у кого есть ссылка (чтобы пользователь мог читать/редактировать)
    permission = {
        'type': 'anyone',
        'role': 'writer'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    
    print(f"Ссылка на Google Doc: {file.get('webViewLink')}")

if __name__ == '__main__':
    upload_to_docs()
