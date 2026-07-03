---
name: connect-automation
description: Интеграция и автоматизация рабочих процессов с использованием N8N, вебхуков и API.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Connect Automation Skill

N8N — инструмент для визуальной автоматизации workflows с поддержкой 400+ интеграций.

## Локальная инфраструктура
- **N8N URL**: `https://<YOUR_N8N_DOMAIN>`
- **Ноды**: HTTP Request, Webhook, Telegram, PostgreSQL, Redis, Execute Command, Code.

## Создание API-эндпоинта через Webhook

### Базовый паттерн
1. **Webhook Node** (триггер) → слушает входящие запросы на указанном URL.
2. **Code/Function Node** → обрабатывает данные из query-параметров или body.
3. **Respond to Webhook Node** → возвращает результат клиенту.

### Передача параметров через URL
```
https://n8n-url/webhook/my-path?first_name=bob&last_name=dylan
```
Параметры доступны в N8N через `{{ $json.query.first_name }}`.

### Пример: отправка данных на Webhook (Node.js)
```javascript
const axios = require('axios');

async function triggerWorkflow(data) {
  try {
    const response = await axios.post(
      'https://<YOUR_N8N_DOMAIN>/webhook/my-path',
      data,
      { headers: { 'Content-Type': 'application/json' } }
    );
    console.log('Success:', response.data);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

### Пример: cURL
```bash
curl -X POST "https://<YOUR_N8N_DOMAIN>/webhook/my-path" \
  -H "Content-Type: application/json" \
  -d '{"event": "user_signup", "userId": 123}'
```

## Продвинутая обработка ошибок

### Error Trigger Workflow
Создай отдельный workflow с нодой **Error Trigger** — он будет ловить все ошибки из других workflows.
```
Error Trigger → Code (форматирование) → Telegram (уведомление)
```

### Retry Logic
- Используй ноду **Wait** + **IF** для повторных попыток при временных сбоях API.
- Паттерн: HTTP Request → IF (status != 200) → Wait (5 сек) → HTTP Request (retry).

### Обработка ошибок в Code Node
```javascript
try {
  const response = await $http.request({
    method: 'GET',
    url: 'https://api.example.com/data',
  });
  return [{ json: response }];
} catch (error) {
  return [{ json: { error: error.message, status: 'failed' } }];
}
```

## HTTP Request Node — продвинутое использование

### Аутентификация
- **Bearer Token**: Header → `Authorization: Bearer {token}`
- **Basic Auth**: Используй встроенные Credentials.
- **API Key**: Header → `X-API-Key: {key}` или Query → `?api_key={key}`

### Pagination (автоматическая)
В настройках HTTP Request включи **Pagination** → Response Contains (Next URL / Offset).

### Ignore SSL Issues
Включай для самоподписанных сертификатов (например, на VPS).

## Безопасность Webhook
- 🚨 Используй **Header Auth** для защиты от неавторизованных вызовов.
- Используй dedicated API-ключи с минимальными привилегиями (least-privilege).
- Ротируй ключи регулярно.
- Ограничивай IP-адреса через Nginx/firewall перед N8N.

## Масштабирование
- Разделяй сложные процессы на мелкие workflows (нода **Execute Workflow**).
- Используй **Queue Mode** для высоконагруженных сценариев.
- Для параллельной обработки используй **Split In Batches**.

## Трансформация данных (Code Node)
```javascript
// Преобразование массива в объект
const result = {};
for (const item of $input.all()) {
  result[item.json.key] = item.json.value;
}
return [{ json: result }];
```

```javascript
// Фильтрация и маппинг
const filtered = $input.all()
  .filter(item => item.json.status === 'active')
  .map(item => ({ json: { name: item.json.name, email: item.json.email } }));
return filtered;
```

## Отладка Workflows
1. **Executions Tab** — просмотр входных/выходных данных каждой ноды.
2. **Pin Data** — зафиксируй тестовые данные для повторного использования.
3. **NoOp Node** — временное отключение частей схемы.
4. Документируй ноды в поле **Notes** (Sticky Notes).
