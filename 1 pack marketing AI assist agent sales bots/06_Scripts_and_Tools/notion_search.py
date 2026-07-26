import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")
MATON_API_KEY = os.getenv("MATON_API_KEY")

headers = {
    "Authorization": f"Bearer {MATON_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

url = "https://gateway.maton.ai/notion/v1/search"
data = {
    "filter": {
        "value": "database",
        "property": "object"
    }
}

print("Поиск баз данных в Notion через Maton API...")
resp = requests.post(url, headers=headers, json=data)

if resp.status_code == 200:
    results = resp.json().get("results", [])
    if results:
        print(f"Найдено баз данных: {len(results)}")
        for db in results:
            title = db.get("title", [{}])[0].get("plain_text", "Без названия") if db.get("title") else "Без названия"
            print(f"- {title} (ID: {db['id']})")
    else:
        print("Базы данных не найдены! Попробуем найти обычные страницы...")
        data["filter"]["value"] = "page"
        resp2 = requests.post(url, headers=headers, json=data)
        if resp2.status_code == 200:
            pages = resp2.json().get("results", [])
            for p in pages[:5]:
                print(f"Страница: ID {p['id']}")
else:
    print(f"Ошибка запроса: {resp.status_code} {resp.text}")
