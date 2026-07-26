import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("ANTIGRAVITY_BOT_TOKEN")
chat_id = "888005446"

if token:
    # Шлем как документ, так как список длинный
    with open("categories_list.txt", "rb") as f:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        resp = requests.post(url, data={"chat_id": chat_id, "caption": "Список 175 категорий из Судебного Кабинета"}, files={"document": f})
        print(resp.json())
else:
    print("Token not found in .env")
