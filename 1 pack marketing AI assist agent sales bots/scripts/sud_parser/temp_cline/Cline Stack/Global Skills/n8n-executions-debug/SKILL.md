---
name: n8n-executions-debug
description: Разбор execution data n8n — анализ failed nodes, input/output, error context, retry стратегии. Используй при диагностике упавших workflows или анализе execution history.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n Executions Debug

## Структура Execution Data

Каждый execution содержит:

```javascript
{
  "id": "123",
  "finished": false,           // true = завершён, false = упал
  "mode": "webhook",           // trigger, webhook, manual, retry
  "startedAt": "2025-...",
  "stoppedAt": "2025-...",
  "workflowId": "42",
  "status": "error",           // success, error, waiting, running
  "data": {
    "resultData": {
      "runData": {             // данные каждой ноды
        "Webhook": [{          // массив — по одному элементу на execution
          "startTime": 1234,
          "executionTime": 50,
          "data": { "main": [[{ "json": {...} }]] },
          "source": []
        }],
        "HTTP Request": [{
          "startTime": 1284,
          "executionTime": 2000,
          "error": {           // ⚠️ Если нода упала — error объект
            "message": "Request failed with status 500",
            "description": "Internal Server Error",
            "httpCode": 500
          }
        }]
      },
      "error": {               // Общая ошибка workflow
        "message": "...",
        "node": { "name": "HTTP Request" }
      }
    }
  }
}
```

## Алгоритм диагностики

### 1. Определить статус
```
status === "error"  → workflow упал, ищи error
status === "success" → workflow завершился, но результат может быть неверным
status === "waiting" → workflow ждёт (webhook response, wait node)
status === "running" → workflow ещё выполняется
```

### 2. Найти упавшую ноду
```javascript
// error.node.name указывает на проблемную ноду
const failedNode = execution.data.resultData.error?.node?.name;
// "HTTP Request", "Code", "Slack", ...
```

### 3. Посмотреть input упавшей ноды
```javascript
// Ищем ноду, которая передала данные в упавшую
const runData = execution.data.resultData.runData;
const prevNodeData = runData["Previous Node"][0].data.main[0];
// Это то, что пришло на вход упавшей ноды
```

### 4. Прочитать error message
```javascript
const error = runData["Failed Node"][0].error;
// error.message — краткое описание
// error.description — подробности
// error.httpCode — HTTP-код (если API)
// error.stack — stack trace (если Code Node)
```

## Частые ошибки по категориям

### HTTP/API ошибки

| HTTP код | Причина | Действие |
|----------|---------|----------|
| **400** | Неверный запрос (body/params) | Проверить формат отправляемых данных |
| **401** | Невалидный токен/ключ | Проверить credentials, не истёк ли токен |
| **403** | Нет доступа | Проверить permissions, scope токена |
| **404** | Ресурс не найден | Проверить URL, ID ресурса |
| **429** | Rate limit | Добавить Wait node или снизить частоту |
| **500** | Ошибка сервера | Retry, проверить API status page |
| **502/503** | Сервис недоступен | Retry с backoff |
| **ETIMEDOUT** | Timeout соединения | Увеличить timeout, проверить сеть |
| **ECONNREFUSED** | Отказ в соединении | Проверить URL/порт, доступность сервиса |

### Code Node ошибки

| Ошибка | Причина | Исправление |
|--------|---------|-------------|
| `TypeError: Cannot read property 'X' of undefined` | Поле не существует | Optional chaining: `item?.json?.X` |
| `ReferenceError: X is not defined` | Переменная не объявлена | Проверить имя переменной |
| `SyntaxError: Unexpected token` | Синтаксическая ошибка JS | Проверить скобки, запятые |
| `The code doesn't return items` | Нет return | Добавить `return [{json: ...}]` |
| `items is not iterable` | Неправильный return формат | Возвращать массив `[{json: ...}]` |

### Expression ошибки

| Ошибка | Причина | Исправление |
|--------|---------|-------------|
| `Cannot read property of undefined` | Путь к данным неверный | Проверить структуру через input panel |
| `X is not a function` | Вызов метода на не-функции | Проверить тип данных |
| Текст выводится буквально | Нет `{{ }}` | Обернуть в двойные скобки |

### Credential ошибки

| Ошибка | Причина | Исправление |
|--------|---------|-------------|
| `Credentials not found` | Credential удалён или переименован | Пересоздать credential |
| `Invalid credentials` | Токен/ключ невалиден | Обновить ключ в настройках |
| `OAuth token expired` | OAuth токен истёк | Переавторизоваться |

## Стратегии Retry

### Встроенный retry (настройка ноды)
```
Node Settings → On Error → Retry On Fail
- Max Tries: 3
- Wait Between Tries: 1000ms
- Backoff: exponential
```

### Ручной retry через workflow
```
1. HTTP Request → IF (status !== 200)
2. IF True → Wait (5 сек) → HTTP Request (retry)
3. IF False → Continue
4. Добавить счётчик попыток через Set node
```

### Retry execution через API
```bash
# Повторить упавший execution
POST /api/v1/executions/{id}/retry

# С другими данными
POST /api/v1/workflows/{id}/run
Content-Type: application/json
{"data": {...}}
```

## Error Trigger Workflow

Отдельный workflow для перехвата ошибок из любых workflows:

```
Error Trigger → Code (форматирование) → Slack/Telegram (уведомление)
```

### Структура данных Error Trigger
```javascript
{
  "execution": {
    "id": "123",
    "url": "https://n8n.example.com/execution/123",
    "error": {
      "message": "Request failed",
      "node": { "name": "HTTP Request", "type": "n8n-nodes-base.httpRequest" }
    },
    "lastNodeExecuted": "HTTP Request",
    "mode": "webhook"
  },
  "workflow": {
    "id": "42",
    "name": "My Workflow"
  }
}
```

### Шаблон уведомления
```javascript
const exec = $json.execution;
const wf = $json.workflow;

const message = `🔴 Ошибка в workflow
📋 ${wf.name} (ID: ${wf.id})
❌ Нода: ${exec.error.node.name}
💬 ${exec.error.message}
🔗 ${exec.url}
⏰ ${new Date().toISOString()}`;

return [{ json: { message } }];
```

## Анализ execution history

### Паттерны для диагностики

**Спорадические ошибки (иногда работает, иногда нет):**
- Rate limiting → добавить throttling
- Таймауты → нестабильная сеть/API
- Race conditions → добавить Wait между вызовами

**Всегда падает на одной ноде:**
- Неправильная конфигурация → проверить параметры
- Сломанные credentials → обновить токены
- Изменённый API → проверить документацию API

**Работало, перестало:**
- API изменил формат ответа → обновить маппинг
- Истёк токен → обновить credentials
- Исчерпан лимит → проверить квоты

**Падает только на определённых данных:**
- Null/undefined в данных → добавить проверки
- Спецсимволы → экранирование
- Слишком большой payload → Split In Batches

## Инструменты диагностики

### Через MCP (n8n-mcp)
```
search_workflows → найти workflow
get_workflow_details → получить структуру
execute_workflow → запустить для теста
```

### Через MCP (n8n-docs)
```
get_node → документация проблемной ноды
validate_node → проверить конфигурацию
validate_workflow → проверить весь workflow
```

### Через n8n UI
1. **Executions tab** — список всех запусков
2. **Клик на execution** — просмотр данных каждой ноды
3. **Input/Output панель** — данные до и после ноды
4. **Error panel** — полный текст ошибки + stack trace

## Live inspection через n8n Public API

Если нужно посмотреть, **что внутри workflow**, без ручного открытия UI, используй Public API n8n.

### Стандартная авторизация

```bash
curl -X GET "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

🚨 Для n8n Public API основной заголовок — **`X-N8N-API-KEY`**, а не `Authorization: Bearer ...`.

### Что обычно нужно от пользователя

- **Base URL инстанса**: `https://your-n8n-host`
- **Public API key**
- **workflow_id** или полный URL вида `https://host/workflow/<id>`
- Если известен **execution_id** — отлично, можно сразу читать execution details

🚨 Стандартный заголовок `X-N8N-API-KEY` я использую сам. Пользователю не нужно отдельно объяснять заголовки, если это обычный n8n Public API.

### Что я могу посмотреть через API

#### Получить workflow целиком
```bash
curl -X GET "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Это даёт:
- `name`
- `active`
- `nodes`
- `connections`
- `settings`
- `versionId`

#### Получить список workflows
```bash
curl -X GET "https://<n8n-host>/api/v1/workflows" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

#### Получить последние executions
```bash
curl -X GET "https://<n8n-host>/api/v1/executions?status=error&limit=10" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Это даёт:
- `id`
- `workflowId`
- `status`
- `mode`
- `startedAt`
- `stoppedAt`

#### Получить execution details с данными
```bash
curl -X GET "https://<n8n-host>/api/v1/executions/<executionId>?includeData=true" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Это может дать:
- `resultData.error`
- `runData`
- `node.name`
- `messages`
- `stack`
- входные/выходные данные нод

Если `execution_id` заранее неизвестен, можно сначала взять список executions и отфильтровать по `workflowId` и времени.

### Важное ограничение

- ✅ `GET /api/v1/workflows/<id>` — normal public API path
- ✅ `GET /api/v1/executions/<id>?includeData=true` позволяет читать execution details и ошибки
- ❌ `/rest/workflows/<id>` часто требует UI session/cookie и может вернуть `401`, даже если API key валиден
- ❌ Public API не даёт container logs / Railway logs / system logs
- Если пользователь прислал только ссылку на UI, но без API key, я не смогу надёжно посмотреть структуру workflow через API

## Проверенный рабочий сценарий диагностики через Public API

Ниже — только то, что уже было успешно подтверждено на живом инстансе:

### Шаг 1. Найти упавшие executions

```bash
curl -X GET "https://<n8n-host>/api/v1/executions?status=error&limit=10" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Это даёт:
- `executionId`
- `workflowId`
- `status`
- `mode`
- `startedAt`
- `stoppedAt`

### Шаг 2. Прочитать execution details с данными

```bash
curl -X GET "https://<n8n-host>/api/v1/executions/<executionId>?includeData=true" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Успешно подтверждено, что через это можно получить:
- `resultData.error.description`
- `messages`
- `stack`
- `node.name`
- параметры проблемной ноды
- runtime context execution

### Шаг 3. Дальше смотреть workflow structure

После нахождения проблемного `workflowId` можно сразу читать workflow:

```bash
curl -X GET "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <your-api-key>"
```

Практический вывод:
- для большинства падений достаточно **URL + API key**;
- `execution_id` полезен, но его можно часто найти самостоятельно через список executions;
- отдельные server/container logs нужны только для инфраструктурных проблем.

## Чек-лист диагностики

- [ ] Определить статус execution (error/success/waiting)
- [ ] Найти имя упавшей ноды
- [ ] Прочитать error message полностью
- [ ] Посмотреть input данные упавшей ноды
- [ ] Проверить credentials (если API-нода)
- [ ] Проверить конфигурацию через validate_node
- [ ] Проверить выражения через input panel
- [ ] Попробовать выполнить с тестовыми данными
- [ ] Если retry помогает → проблема временная (rate limit, timeout)
- [ ] Если retry не помогает → проблема в конфигурации
