import json
import sys
import os
import requests

# Мастер-ключ для авторизации нашего MCP-сервера в API
API_URL = "http://localhost:8000"  # На VPS это будет локальный порт
API_KEY = os.getenv("AI_LAWYER_API_KEY", "kz_lawyer_master_secret_2026")

def search_cases_api(iin_or_bin: str, year: str = "2025") -> dict:
    """Делает запрос к нашему FastAPI-ядру."""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "iin_or_bin": iin_or_bin,
            "year": year
        }
        # Если запущено локально на VPS, делаем запрос к локальному FastAPI
        response = requests.post(f"{API_URL}/api/v1/cases/search", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": f"API returned status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def handle_request(req):
    """Обработчик протокола MCP (JSON-RPC 2.0)."""
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "kazakhstan-court-acts-mcp",
                    "version": "1.0.0"
                }
            }
        }
        
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "search_court_cases",
                        "description": "Поиск судебных дел и актов в Республике Казахстан по БИН или ИИН компании/гражданина.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "iin_or_bin": {
                                    "type": "string",
                                    "description": "12-значный ИИН или БИН контрагента для поиска."
                                },
                                "year": {
                                    "type": "string",
                                    "description": "Год поиска судебных актов (по умолчанию 2025)."
                                }
                            },
                            "required": ["iin_or_bin"]
                        }
                    }
                ]
            }
        }
        
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "search_court_cases":
            iin_or_bin = arguments.get("iin_or_bin")
            year = arguments.get("year", "2025")
            
            if not iin_or_bin or len(iin_or_bin) != 12 or not iin_or_bin.isdigit():
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Ошибка: ИИН или БИН должен состоять ровно из 12 цифр."
                            }
                        ],
                        "isError": True
                    }
                }
                
            api_result = search_cases_api(iin_or_bin, year)
            
            # Красиво форматируем вывод для ИИ-агента
            if api_result.get("success"):
                cases = api_result.get("cases", [])
                if not cases:
                    text_response = f"Судебных дел для ИИН/БИН {iin_or_bin} не найдено."
                else:
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
            else:
                text_response = f"Не удалось выполнить поиск. Ошибка: {api_result.get('error', 'Unknown error')}"
                
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": text_response
                        }
                    ]
                }
            }
            
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Метод {method} не найден"
        }
    }

def main():
    """Основной цикл чтения команд из стандартного ввода (stdio mcp)."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            # Логируем ошибки в stderr, чтобы не засорять stdout (протокол mcp идет строго через stdout)
            sys.stderr.write(f"Error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
