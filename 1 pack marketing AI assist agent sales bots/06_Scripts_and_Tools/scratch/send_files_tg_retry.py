import requests
import time

TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
URL = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

files_to_send = [
    "cv_hunt_career/CRM_marketer/dataset_crm.csv",
    "cv_hunt_career/CRM_marketer/run_analysis.py",
    "cv_hunt_career/CRM_marketer/task_description.md"
]

for file_path in files_to_send:
    success = False
    retries = 3
    while not success and retries > 0:
        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": CHAT_ID}
                response = requests.post(URL, files=files, data=data, timeout=15)
                if response.status_code == 200:
                    print(f"✅ Успешно отправлено: {file_path}")
                    success = True
                else:
                    print(f"❌ Ошибка API для {file_path}: {response.text}")
                    retries -= 1
                    time.sleep(3)
        except Exception as e:
            print(f"⚠️ Сетевая ошибка при отправке {file_path}: {str(e)}")
            retries -= 1
            time.sleep(3)
