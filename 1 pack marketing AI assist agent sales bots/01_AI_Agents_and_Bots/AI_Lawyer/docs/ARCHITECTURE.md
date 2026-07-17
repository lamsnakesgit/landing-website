# Архитектура API-моста для ИИ-платформ и CRM

## Обзор архитектуры
Система представляет собой универсальный шлюз (API), который позволяет ИИ-агентам (ChatGPT Actions, Claude MCP), CRM-системам и Telegram-ботам получать структурированные данные судебных дел с портала `sud.kz`.

```
[Пользователь / ИИ / CRM] 
       │ (HTTP Request / JSON-RPC)
       ▼
[FastAPI API Bridge на VPS (Port 8000)]
       │ (Запуск Playwright / Kalkan Docker)
       ▼
[Портал sud.kz]
```

## Компоненты системы

### 1. API Core (`src/app.py`)
* **Технологии**: FastAPI, Uvicorn, Pydantic.
* **Хост**: VPS `151.244.228.104:8000`.
* **Авторизация**: Заголовок `Authorization: Bearer <API_KEY>`. Мастер-ключ задается переменной окружения `AI_LAWYER_API_KEY` (по умолчанию `kz_lawyer_master_secret_2026`).
* **Эндпоинты**:
  * `GET /health` — проверка работоспособности.
  * `POST /api/v1/cases/search` — поиск дел по ИИН/БИН.

### 2. MCP Server (`src/mcp_server.py`)
* **Технологии**: Python (Stdio).
* **Назначение**: Коннектор для Claude Desktop и Cursor.
* **Инструменты (Tools)**:
  * `search_court_cases` — принимает `iin_or_bin` (12 цифр) и `year`. Транслирует вызов в HTTP-запрос к API Core.

### 3. Схема OpenAPI (`openapi_schema.json`)
* **Назначение**: Импорт в Custom GPT Actions на платформе OpenAI (ChatGPT Store).

## Настройки VPS (151.244.228.104)
* **Директория проекта**: `/root/ai_lawyer`
* **Команда запуска**:
  `nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > /root/ai_lawyer/logs/api.log 2>&1 &`
* **Логи API**: `/root/ai_lawyer/logs/api.log`
