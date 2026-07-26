import os
import sys
import requests
from dotenv import load_dotenv

def find_party(query, api_key, country="ru"):
    """
    Поиск компании по названию в DaData.
    country = "ru" (Россия) или "kz" (Казахстан)
    """
    if country == "kz":
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party_kz"
    else:
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party"
        
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {api_key}"
    }
    
    data = {
        "query": query
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            suggestions = response.json().get("suggestions", [])
            if not suggestions:
                print(f"[-] Компании не найдены для '{query}' ({country})")
                return None
            
            first = suggestions[0]
            val = first.get("value")
            d = first.get("data", {})
            
            # Извлекаем БИН/ИНН, Руководителя
            if country == "kz":
                bin_num = d.get("bin")
                director = d.get("management_name")
            else:
                bin_num = d.get("inn")
                management = d.get("management", {})
                director = management.get("name") if management else None
                
            print(f"[+] Найдено ({country}): {val}")
            print(f"    Идентификатор: {bin_num}")
            print(f"    Руководитель: {director}")
            return {
                "name": val,
                "id": bin_num,
                "director": director
            }
        else:
            print(f"[-] Ошибка DaData Suggestions ({country}): {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[!] Исключение при запросе DaData ({country}): {e}")
        return None

def main():
    load_dotenv()
    api_key = os.getenv("DADATA_API_KEY")
    if not api_key:
        print("[!] DADATA_API_KEY не задан в .env")
        return
        
    print("=== Тест DaData KZ ===")
    find_party("Стройшахтопроект", api_key, "kz")
    
    print("\n=== Тест DaData RU ===")
    find_party("Грин-Апи", api_key, "ru")

if __name__ == "__main__":
    main()
