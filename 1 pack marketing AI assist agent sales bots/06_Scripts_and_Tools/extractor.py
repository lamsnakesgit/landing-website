import os
import json
import glob
from google import genai
from google.genai import types
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Нужен service_role для обхода RLS или добавления данных

if not all([GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Не установлены переменные окружения! Проверьте .env файл.")
    exit(1)

# Инициализация клиентов
ai_client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_embedding(text: str) -> list[float]:
    """Получает вектор (768 измерений) для текста через Gemini"""
    response = ai_client.models.embed_content(
        model='text-embedding-004',
        contents=text,
    )
    return response.embeddings[0].values

def summarize_case(case_data: dict, full_text: str = "") -> str:
    """Опциональная функция: сжать длинный PDF в короткое саммари, чтобы улучшить вектор"""
    # Пока мы просто склеиваем метаданные для вектора, 
    # так как извлечение полного текста из PDF/DOCX будет реализовано позже 
    # (или через pdfplumber/python-docx)
    summary = f"Дело № {case_data.get('case_num')}. Истец: {case_data.get('plaintiff')}. Ответчик: {case_data.get('defendant')}. Судья: {case_data.get('judge')}. Категория: {case_data.get('category', 'Трудовой спор')}. "
    return summary

def main():
    JSON_FILE = "scripts/sud_parser/kalkan_docker/output/labor_cases.json"
    
    if not os.path.exists(JSON_FILE):
        print(f"Файл {JSON_FILE} не найден. Убедитесь, что парсер уже отработал.")
        return
        
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print(f"Найдено {len(cases)} дел в JSON. Начинаем векторизацию...")
    
    for case in cases:
        case_num = case.get("case_num", "")
        year = case.get("date", "2024")[:4]
        
        # 1. Генерируем текст для вектора (пока только из метаданных, позже добавим текст из файлов)
        text_to_embed = summarize_case(case)
        
        # 2. Получаем вектор
        try:
            print(f"Получение вектора для {case_num}...")
            embedding = get_embedding(text_to_embed)
        except Exception as e:
            print(f"⚠️ Ошибка Gemini API для {case_num}: {e}")
            continue
            
        # 3. Сохраняем в Supabase
        data_to_insert = {
            "case_number": case_num,
            "year": int(year),
            "judge": case.get("judge", ""),
            "plaintiff": case.get("plaintiff", ""),
            "defendant": case.get("defendant", ""),
            "category": case.get("category", ""),
            "summary": text_to_embed,
            "original_url": f"https://office.sud.kz/lawsuit/...", # Можно уточнить логику формирования ссылки
            "embedding": embedding
        }
        
        try:
            response = supabase.table("cases").insert(data_to_insert).execute()
            print(f"✅ Успешно загружено в Supabase: {case_num}")
        except Exception as e:
            print(f"❌ Ошибка вставки в Supabase {case_num}: {e}")

if __name__ == "__main__":
    main()
