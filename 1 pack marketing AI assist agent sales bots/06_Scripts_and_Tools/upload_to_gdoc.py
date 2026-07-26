import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
MATON_API_KEY = os.environ.get('MATON_API_KEY')

files = [f"temp_cases/case_{i}.html" for i in range(2, 7)]
links = []

for file_path in files:
    if not os.path.exists(file_path):
        continue
    url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?fields=id,webViewLink"
    metadata = {
        "name": f"Судебное Дело - {os.path.basename(file_path)}",
        "mimeType": "application/vnd.google-apps.document"
    }
    
    with open(file_path, "rb") as f:
        upload_files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (file_path, f, "text/html")
        }
        
        response = requests.post(
            f"{url}&uploadType=multipart",
            headers={"Authorization": f"Bearer {MATON_API_KEY}"},
            files=upload_files
        )
        
        if response.status_code == 200:
            data = response.json()
            link = data.get('webViewLink')
            file_id = data.get('id')
            
            # Share
            perm_url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{file_id}/permissions"
            requests.post(
                perm_url,
                headers={
                    "Authorization": f"Bearer {MATON_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"role": "reader", "type": "anyone"}
            )
            
            links.append(link)
        else:
            print(f"ERROR on {file_path}:", response.status_code, response.text)

print(json.dumps(links))
