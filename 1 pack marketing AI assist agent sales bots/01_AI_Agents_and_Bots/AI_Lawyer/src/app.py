import os
import asyncio
import subprocess
import json
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="Kazakhstan Court Acts AI Bridge API",
    description="Универсальный API-мост для поиска судебных дел и актов в Республике Казахстан (sud.kz) через ЭЦП.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Считываем мастер-ключ из .env / окружения
MASTER_API_KEY = os.getenv("AI_LAWYER_API_KEY", "kz_lawyer_master_secret_2026")
ECP_PASSWORD = os.getenv("ECP_PASSWORD", "Prioritize_resource3!")

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не предоставлен API-ключ в заголовке Authorization"
        )
    clean_key = api_key.replace("Bearer ", "") if api_key.startswith("Bearer ") else api_key
    if clean_key != MASTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API-ключ"
        )
    return clean_key

class CaseSearchRequest(BaseModel):
    iin_or_bin: str = Field(..., description="ИИН или БИН контрагента для поиска судебных дел", example="123456789012")
    year: Optional[str] = Field("2025", description="Год поиска судебных актов", example="2025")
    max_results: Optional[int] = Field(20, description="Максимальное количество результатов", example=10)

class CourtCase(BaseModel):
    case_number: str = Field(..., description="Номер дела")
    court: str = Field(..., description="Судебный орган")
    category: str = Field(..., description="Категория дела")
    parties: str = Field(..., description="Стороны по делу")
    judge: str = Field(..., description="Судья")
    date: str = Field(..., description="Дата регистрации/решения")
    result: str = Field(..., description="Результат рассмотрения")
    links: Optional[List[str]] = Field(default=[], description="Ссылки на судебные акты/файлы")

class CaseSearchResponse(BaseModel):
    success: bool
    query_iin_bin: str
    total_found: int
    cases: List[CourtCase]
    error: Optional[str] = None

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "API Bridge работает исправно, Docker доступен"}

@app.post("/api/v1/cases/search", response_model=CaseSearchResponse, tags=["Search"])
async def search_cases(request: CaseSearchRequest, api_key: str = Depends(get_api_key)):
    """
    Поиск судебных дел по ИИН/БИН контрагента на портале sud.kz с реальной авторизацией ЭЦП через Docker.
    """
    print(f"Запуск реального поиска в Docker по ИИН/БИН: {request.iin_or_bin} (Год: {request.year})")
    
    # Формируем команду запуска Docker с вызовом нашего API-воркера
    docker_cmd = [
        "docker", "run", "--rm",
        "-e", f"ECP_PASSWORD={ECP_PASSWORD}",
        "-e", "PYTHONUNBUFFERED=1",
        "-v", "/root/ai_lawyer:/app",
        "-v", "/root/ai_lawyer/output:/output",
        "-v", "/root/ai_lawyer/keys:/keys",
        "-v", "/root/ai_lawyer/kalkan_test:/app_temp",
        "-w", "/app",
        "playwright_kalkan",
        "python3", "src/search_cases_api.py", request.iin_or_bin, request.year
    ]
    
    try:
        # Запускаем процесс асинхронно, чтобы не блокировать поток FastAPI
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_msg = stderr.decode(encoding="utf-8", errors="ignore")
            print(f"Ошибка Docker: {err_msg}")
            return CaseSearchResponse(
                success=False,
                query_iin_bin=request.iin_or_bin,
                total_found=0,
                cases=[],
                error=f"Ошибка выполнения Docker контейнера: {err_msg}"
            )
            
        # Парсим JSON из stdout воркера
        output_str = stdout.decode(encoding="utf-8", errors="ignore").strip()
        print(f"Ответ воркера: {output_str}")
        
        # Находим первую строчку, содержащую JSON-структуру (на случай лишних принтов)
        json_start = output_str.find('{"success"')
        if json_start != -1:
            output_str = output_str[json_start:]
            
        data = json.loads(output_str)
        
        if not data.get("success"):
            return CaseSearchResponse(
                success=False,
                query_iin_bin=request.iin_or_bin,
                total_found=0,
                cases=[],
                error=data.get("error", "Неизвестная ошибка воркера")
            )
            
        cases_list = [
            CourtCase(
                case_number=c["case_number"],
                court=c["court"],
                category=c["category"],
                parties=c["parties"],
                judge=c["judge"],
                date=c["date"],
                result=c["result"],
                links=c.get("links", [])
            ) for c in data.get("cases", [])
        ]
        
        return CaseSearchResponse(
            success=True,
            query_iin_bin=request.iin_or_bin,
            total_found=len(cases_list),
            cases=cases_list
        )
        
    except Exception as e:
        print(f"Исключение при поиске: {str(e)}")
        return CaseSearchResponse(
            success=False,
            query_iin_bin=request.iin_or_bin,
            total_found=0,
            cases=[],
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
