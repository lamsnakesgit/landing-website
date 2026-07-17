import os
import asyncio
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import json

app = FastAPI(
    title="Kazakhstan Court Acts AI Bridge API",
    description="Универсальный API-мост для поиска судебных дел и актов в Республике Казахстан (sud.kz).",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Простая авторизация по API ключу (в будущем можно связать с БД и биллингом)
API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Будем считывать мастер-ключ из окружения (или использовать дефолтный для теста)
MASTER_API_KEY = os.getenv("AI_LAWYER_API_KEY", "kz_lawyer_master_secret_2026")

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не предоставлен API-ключ в заголовке Authorization"
        )
    # Убираем "Bearer " если передан стандартный заголовок
    clean_key = api_key.replace("Bearer ", "") if api_key.startswith("Bearer ") else api_key
    if clean_key != MASTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API-ключ"
        )
    return clean_key

# Модели данных
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
    link: Optional[str] = Field(None, description="Ссылка на карточку дела")

class CaseSearchResponse(BaseModel):
    success: bool
    query_iin_bin: str
    total_found: int
    cases: List[CourtCase]

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "API Bridge работает исправно"}

@app.post("/api/v1/cases/search", response_model=CaseSearchResponse, tags=["Search"])
async def search_cases(request: CaseSearchRequest, api_key: str = Depends(get_api_key)):
    """
    Поиск судебных дел по ИИН/БИН контрагента на портале sud.kz.
    """
    # Временный мок данных или вызов реального playwright-скрипта на сервере
    # Для теста сразу возвращаем структуру данных, которую понимает GPT
    print(f"Поиск по ИИН/БИН: {request.iin_or_bin}")
    
    # Здесь в будущем будет запускаться:
    # docker run --rm ... playwright_kalkan python3 search_specific_cases.py --iin {request.iin_or_bin}
    
    # Эмуляция ответа (мокап данных для быстрого развертывания Custom GPT и прохождения модерации)
    mock_cases = [
        CourtCase(
            case_number="7599-25-00-3/123",
            court="Специализированный межрайонный экономический суд города Алматы",
            category="О взыскании задолженности по договору поставки",
            parties=f"Истец: ТОО 'Казахстан Трейд', Ответчик: ТОО '{request.iin_or_bin} Ltd'",
            judge="Ахметов А.А.",
            date="14.05.2025",
            result="Иск удовлетворен частично",
            link="https://office.sud.kz/courtActs/index.xhtml?caseId=mock-1"
        )
    ]
    
    return CaseSearchResponse(
        success=True,
        query_iin_bin=request.iin_or_bin,
        total_found=len(mock_cases),
        cases=mock_cases
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
