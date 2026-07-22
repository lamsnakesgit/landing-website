import os
import requests
from mcp.server.fastmcp import FastMCP

# Создаем MCP сервер
mcp = FastMCP("kazakhstan-court-acts-mcp")

@mcp.tool()
def search_court_cases(iin_or_bin: str, year: str = "2025") -> str:
    """Поиск судебных дел и актов в Республике Казахстан по БИН или ИИН компании/гражданина."""
    
    try:
        API_URL = "http://localhost:8000"
        API_KEY = os.getenv("AI_LAWYER_API_KEY", "kz_lawyer_master_secret_2026")
        
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
            return f"API Error: {response.status_code} - {response.text}"
            
        data = response.json()
        if not data.get("success"):
            return f"Error: {data.get('error')}"
            
        cases = data.get("cases", [])
        if not cases:
            return f"Судебных дел для ИИН/БИН {iin_or_bin} не найдено."
            
        text_response = f"Найденные судебные дела ({len(cases)}): \n"
        for idx, case in enumerate(cases, 1):
            text_response += (
                f"\n{idx}. Дело №: {case['case_number']}\n"
                f"   Суд: {case['court']}\n"
                f"   Категория: {case['category']}\n"
                f"   Стороны: {case['parties']}\n"
                f"   Судья: {case['judge']}\n"
                f"   Результат: {case['result']}\n"
                f"   Дата: {case['date']}\n"
            )
            
        return text_response
        
    except Exception as e:
        return f"Internal Server Error: {str(e)}"

# Этот файл можно запустить локально
# По умолчанию FastMCP.run() запускается в режиме stdio
# Но мы можем запустить его в режиме sse через командную строку или метод mcp.run(transport='sse')

if __name__ == "__main__":
    # Запускаем сервер по протоколу SSE на порту 8001 через uvicorn
    print("Запускаем Web MCP Сервер (SSE) на порту 8001...")
    import uvicorn
    uvicorn.run(mcp._app if hasattr(mcp, '_app') else mcp.sse_app, host="0.0.0.0", port=8001)
