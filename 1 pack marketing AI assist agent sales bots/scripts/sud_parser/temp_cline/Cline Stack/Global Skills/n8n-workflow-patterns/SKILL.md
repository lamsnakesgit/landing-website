---
name: n8n-workflow-patterns
description: Архитектурные паттерны n8n workflows — webhook processing, HTTP API, БД, AI Agent, scheduled tasks. Используй при проектировании новых workflows или выборе структуры автоматизации.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n Workflow Patterns

## 5 основных паттернов

### 1. Webhook Processing (самый частый — 35%)
```
Webhook → Validate → Transform → Respond/Notify
```
- Приём данных от внешних систем (формы, Stripe, GitHub)
- Мгновенная реакция на события
- 🚨 Данные в `$json.body`, не в `$json`

### 2. HTTP API Integration
```
Trigger → HTTP Request → Transform → Action → Error Handler
```
- Получение данных из REST API
- Синхронизация с внешними сервисами
- Пример: GitHub Issues → Transform → Jira Tickets

### 3. Database Operations
```
Schedule → Query → Transform → Write → Verify
```
- Синхронизация между БД
- ETL-пайплайны
- Пример: Postgres → Transform → MySQL

### 4. AI Agent Workflow
```
Trigger → AI Agent (Model + Tools + Memory) → Output
```
- Разговорные AI
- Мультишаговые задачи с инструментами
- Пример: Чат-бот с доступом к БД и API

### 5. Scheduled Tasks (28%)
```
Schedule → Fetch → Process → Deliver → Log
```
- Регулярные отчёты
- Периодический сбор данных
- Пример: Ежедневная аналитика → Email

## Выбор паттерна

| Задача | Паттерн |
|--------|---------|
| Принимаю данные от внешних систем | Webhook Processing |
| Забираю данные из API | HTTP API Integration |
| Синхронизирую БД / ETL | Database Operations |
| Строю AI-ассистента с инструментами | AI Agent Workflow |
| Периодическая задача по расписанию | Scheduled Tasks |

## Строительные блоки

### Триггеры
- **Webhook** — HTTP-эндпоинт (мгновенный)
- **Schedule** — Cron (периодический)
- **Manual** — Клик для тестирования
- **Polling** — Проверка изменений по интервалу

### Трансформация
- **Set** — маппинг полей
- **Code** — сложная логика (JS/Python)
- **IF/Switch** — условная маршрутизация
- **Merge** — объединение потоков данных

### Обработка ошибок
- **Error Trigger** — перехват ошибок workflow
- **IF** — проверка условий ошибки
- **Stop and Error** — явный сбой
- **Continue On Fail** — настройка на уровне ноды

## Паттерны потока данных

### Линейный
```
Trigger → Transform → Action → End
```

### Ветвление
```
Trigger → IF → [True Path]
             └→ [False Path]
```

### Параллельная обработка
```
Trigger → [Branch 1] → Merge
       └→ [Branch 2] ↗
```

### Цикл (батчи)
```
Trigger → Split in Batches → Process → Loop (until done)
```

### Error Handler
```
Main Flow → [Success Path]
         └→ [Error Trigger → Handler → Notify]
```

## Примеры

### Webhook → Slack
```
1. Webhook (path: "form-submit", POST)
2. Set (маппинг полей формы)
3. Slack (сообщение в #notifications)
```

### Ежедневный отчёт
```
1. Schedule (ежедневно в 9:00)
2. HTTP Request (получить аналитику)
3. Code (агрегировать данные)
4. Email (отправить отчёт)
5. Error Trigger → Slack (уведомление об ошибке)
```

### Синхронизация БД
```
1. Schedule (каждые 15 мин)
2. Postgres (новые записи)
3. IF (проверить наличие записей)
4. MySQL (вставить записи)
5. Postgres (обновить timestamp синхронизации)
```

### AI-ассистент
```
1. Webhook (получить сообщение чата)
2. AI Agent
   ├─ OpenAI Chat Model (ai_languageModel)
   ├─ HTTP Request Tool (ai_tool)
   ├─ Database Tool (ai_tool)
   └─ Window Buffer Memory (ai_memory)
3. Webhook Response (ответ AI)
```

### API-интеграция с батчами
```
1. Manual Trigger (для тестов)
2. HTTP Request (GET /api/users)
3. Split In Batches (по 100)
4. Set (трансформация данных)
5. Postgres (upsert)
6. Loop (назад к шагу 3)
```

## Проверенные рабочие рецепты через n8n Public API

### 1. Создать простой учебный pipeline

Успешно подтверждённый минимальный шаблон:

```
Manual Trigger → Set → HTTP Request → Set
```

Что показывает этот паттерн:
- ручной запуск;
- подготовку данных через `Set`;
- внешний API вызов через `HTTP Request`;
- финальную нормализацию результата через второй `Set`.

### 2. Обновлять workflow безопасно через API

Проверенный порядок действий:

1. Прочитать текущий workflow через `GET /api/v1/workflows/<id>`
2. Взять его как основу
3. Изменить только нужные `nodes` / `connections` / `settings`
4. Отправить обновлённую версию через `PUT /api/v1/workflows/<id>`
5. Проверить, что вернулся новый `versionId`

🚨 Практическое правило: при update не редактируй workflow “вслепую”. Сначала читай текущую структуру, потом меняй нужные куски.

### 3. Проверенный сложный учебный паттерн

Успешно собран учебный AI-аналитик в виде двух workflow:

**Main workflow:**
```
Chat Trigger → AI Agent
              ├─ Gemini Chat Model
              ├─ Buffer Memory
              ├─ Calculator Tool
              └─ Tool Workflow
```

**Sub-workflow:**
```
Execute Workflow Trigger → Code
```

Этот паттерн хорош для учебного стенда, потому что:
- показывает AI Agent + tools + memory;
- не зависит от внешней БД;
- позволяет держать учебный датасет внутри Code node;
- демонстрирует архитектуру main workflow + sub-workflow.

## Чек-лист создания workflow

### Планирование
- [ ] Определить паттерн (webhook, API, DB, AI, scheduled)
- [ ] Составить список нод
- [ ] Спланировать поток данных (вход → обработка → выход)
- [ ] Спланировать обработку ошибок

### Реализация
- [ ] Создать workflow с подходящим триггером
- [ ] Добавить источники данных
- [ ] Настроить аутентификацию/credentials
- [ ] Добавить ноды трансформации (Set, Code, IF)
- [ ] Добавить выходные ноды
- [ ] Настроить обработку ошибок

### Валидация
- [ ] Проверить конфигурацию каждой ноды
- [ ] Валидировать весь workflow
- [ ] Протестировать с тестовыми данными
- [ ] Обработать крайние случаи (пустые данные, ошибки)

### Деплой
- [ ] Проверить настройки (execution order, timeout)
- [ ] Активировать workflow
- [ ] Мониторить первые выполнения
- [ ] Задокументировать workflow (notes)

## Частые проблемы

| Проблема | Решение |
|----------|---------|
| Не могу получить данные webhook | Данные под `$json.body` |
| Нода обрабатывает все элементы | Используй "Execute Once" или `$json[0]` |
| API возвращает 401/403 | Проверь credentials, используй секцию "Credentials" |
| Ноды выполняются в неверном порядке | Execution Order → v1 (connection-based) |
| Выражения показываются как текст | Оберни в `{{ }}` |

## Статистика

**Триггеры**: Webhook 35%, Schedule 28%, Manual 22%, Service 15%

**Трансформации**: Set 68%, Code 42%, IF 38%, Switch 18%

**Выходы**: HTTP Request 45%, Slack 32%, Database 28%, Email 24%

**Сложность**: Простые (3-5 нод) 42%, Средние (6-10) 38%, Сложные (11+) 20%

## Правила

### ✅ Делай
- Начинай с простейшего подходящего паттерна
- Планируй структуру до реализации
- Добавляй обработку ошибок во все workflows
- Тестируй перед активацией
- Используй описательные имена нод
- Документируй сложные workflows (поле notes)

### ❌ Не делай
- Не строй workflow за один раз — итерируй
- Не пропускай валидацию
- Не игнорируй сценарии ошибок
- Не хардкодь credentials в параметрах
- Не забывай обрабатывать пустые данные
