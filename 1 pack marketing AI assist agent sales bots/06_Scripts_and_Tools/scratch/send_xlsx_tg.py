import requests

TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
URL = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

file_path = "cv_hunt_career/CRM_marketer/RFM_Analysis_Intertop.xlsx"

try:
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": "📊 Эксель-файл с готовой Сводной таблицей (RFM) и фильтрами по сегментам!"}
        response = requests.post(URL, files=files, data=data)
        if response.status_code == 200:
            print(f"✅ Успешно отправлено: {file_path}")
        else:
            print(f"❌ Ошибка отправки: {response.text}")
except Exception as e:
    print(f"⚠️ Ошибка: {str(e)}")
