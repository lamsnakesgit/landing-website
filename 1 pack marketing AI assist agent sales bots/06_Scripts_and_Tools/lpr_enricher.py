import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from duckduckgo_search import DDGS
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY.strip().rstrip('.'))
else:
    openai_client = None

def search_duckduckgo(query, max_results=3):
    """Выполняет поиск через DuckDuckGo и возвращает сниппеты"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

def enrich_lead_data(company_name):
    """
    Основная функция для агента: Ищет ФИО генерального директора и контакты.
    Возвращает JSON строку с извлеченными данными.
    """
    if not openai_client:
        return json.dumps({"error": "OPENAI_API_KEY не настроен."})

    print(f"[*] Обогащение данных для: {company_name}")
    
    # 1. Формируем запрос для поиска ЛПР
    query = f'"{company_name}" ИНН генеральный директор учредитель контакты'
    print(f"[*] Выполняю поиск: {query}")
    
    search_results = search_duckduckgo(query, max_results=5)
    
    if not search_results or "Ошибка поиска" in search_results:
        return json.dumps({
            "company_name": company_name,
            "error": "Не удалось найти информацию в поисковых системах",
            "raw_search": search_results
        })

    # 2. Анализируем сниппеты через OpenAI
    prompt = f"""
    Ты - OSINT-аналитик и 리догенератор. Твоя задача вытащить имя Лица Принимающего Решения (Генеральный директор, Основатель, Учредитель) 
    из предоставленных сниппетов поиска.
    
    Компания: {company_name}
    
    Сниппеты:
    {search_results}
    
    Извлеки:
    1. ФИО ЛПР (если есть).
    2. Должность.
    3. ИНН компании (если упоминается).
    4. Любые личные контакты ЛПР, если вдруг попались в тексте (телефон, email, telegram).
    
    Ответь ТОЛЬКО в формате JSON:
    {{
        "lpr_name": "ФИО или null",
        "position": "Генеральный директор или null",
        "inn": "ИНН или null",
        "contacts": "Найденные контакты или null"
    }}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        
        extracted_data = response.choices[0].message.content
        data_dict = json.loads(extracted_data)
        data_dict['company_name'] = company_name
        return json.dumps(data_dict, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Ошибка OpenAI: {str(e)}"})

if __name__ == "__main__":
    # Тестовый запуск
    test_company = "ООО Ладос-Мебель"
    if len(sys.argv) > 1:
        test_company = " ".join(sys.argv[1:])
        
    result = enrich_lead_data(test_company)
    print("\n--- Результат обогащения ---")
    print(result)
