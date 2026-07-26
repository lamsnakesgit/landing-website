import requests
import time

TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
URL = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

files_to_send = [
    "cv_hunt_career/CRM_marketer/CRM_Loyalty_Presentation.pptx",
    "cv_hunt_career/CRM_marketer/dataset_crm.csv",
    "cv_hunt_career/CRM_marketer/run_analysis.py",
    "cv_hunt_career/CRM_marketer/task_description.md"
]

for file_path in files_to_send:
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID}
            response = requests.post(URL, files=files, data=data)
            if response.status_code == 200:
                print(f"✅ Успешно отправлено: {file_path}")
            else:
                print(f"❌ Ошибка отправки {file_path}: {response.text}")
        time.sleep(1) # Небольшая пауза, чтобы не словить лимиты Телеграма
    except Exception as e:
        print(f"⚠️ Ошибка при чтении файла {file_path}: {str(e)}")
