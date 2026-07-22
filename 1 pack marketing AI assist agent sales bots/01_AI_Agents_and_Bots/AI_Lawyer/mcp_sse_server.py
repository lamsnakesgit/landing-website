from mcp.server.fastmcp import FastMCP
import os
import requests

# Инициализация FastMCP сервера
mcp = FastMCP("kazakhstan-court-acts-mcp")

API_URL = "http://localhost:8000"
API_KEY = os.getenv("AI_LAWYER_API_KEY", "kz_lawyer_master_secret_2026")

@mcp.tool()
def search_court_cases(iin_or_bin: str, year: str = "2025") -> str:
    """Поиск судебных дел и актов в Республике Казахстан по БИН или ИИН компании/гражданина.
    
    Args:
        iin_or_bin: 12-значный ИИН или БИН контрагента для поиска.
        year: Год поиска судебных актов (по умолчанию 2025).
    """
    if not iin_or_bin or len(iin_or_bin) != 12 or not iin_or_bin.isdigit():
        return "Ошибка: ИИН или БИН должен состоять ровно из 12 цифр."
        
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "iin_or_bin": iin_or_bin,
            "year": year
        }
        response = requests.post(f"{API_URL}/api/v1/cases/search", json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return f"Не удалось выполнить поиск. Ошибка API: {response.status_code} - {response.text}"
            
        api_result = response.json()
        
        if api_result.get("success"):
            cases = api_result.get("cases", [])
            if not cases:
                return f"Судебных дел для ИИН/БИН {iin_or_bin} не найдено."
                
            text_response = f"Найденные судебные дела ({len(cases)}): \n"
            for idx, case in enumerate(cases, 1):
                text_response += (
                    f"\n{idx}. Дело №: {case.get('case_number', 'N/A')}\n"
                    f"   Суд: {case.get('court', 'N/A')}\n"
                    f"   Категория: {case.get('category', 'N/A')}\n"
                    f"   Стороны: {case.get('parties', 'N/A')}\n"
                    f"   Судья: {case.get('judge', 'N/A')}\n"
                    f"   Результат: {case.get('result', 'N/A')}\n"
                    f"   Дата: {case.get('date', 'N/A')}\n"
                )
            return text_response
        else:
            return f"Не удалось выполнить поиск. Ошибка: {api_result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Критическая ошибка при поиске: {str(e)}"

if __name__ == "__main__":
    # Запускаем сервер по SSE на порту 8001 (слушает на всех интерфейсах)
    print("Starting FastMCP SSE server on port 8001...")
    mcp.run(transport='sse')
