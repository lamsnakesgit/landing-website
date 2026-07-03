---
name: n8n-http-request
description: HTTP Request node в n8n — аутентификация, headers, pagination, retries, rate limits, обработка ответов. Используй при настройке HTTP-запросов или отладке API-интеграций в n8n.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n HTTP Request Node

## Базовая настройка

```
Method: GET | POST | PUT | PATCH | DELETE | HEAD | OPTIONS
URL: https://api.example.com/endpoint
```

### Отправка данных (POST/PUT/PATCH)

**JSON Body:**
```json
{
  "name": "={{$json.body.name}}",
  "email": "={{$json.body.email}}"
}
```

**Form Data:**
```
Content-Type: multipart/form-data
Field 1: name = value
Field 2: file = binary data
```

**URL-Encoded:**
```
Content-Type: application/x-www-form-urlencoded
key1=value1&key2=value2
```

## Аутентификация

### Bearer Token
```
Authentication → Predefined Credential Type → Header Auth
Header Name: Authorization
Header Value: Bearer {token}
```

Или через Generic Credential:
```
Header Auth → Name: Authorization, Value: Bearer {{$env.API_TOKEN}}
```

### API Key
```
// В Header
Header Name: X-API-Key
Header Value: {{$env.API_KEY}}

// В Query
URL: https://api.example.com/data?api_key={{$env.API_KEY}}
```

### Basic Auth
```
Authentication → Basic Auth
Username: {{$env.API_USER}}
Password: {{$env.API_PASS}}
```

### OAuth2
```
Authentication → OAuth2
Grant Type: Authorization Code | Client Credentials
Authorization URL: https://provider.com/oauth/authorize
Access Token URL: https://provider.com/oauth/token
Client ID: {{$env.OAUTH_CLIENT_ID}}
Client Secret: {{$env.OAUTH_CLIENT_SECRET}}
Scope: read write
```

### Custom Headers
```
Headers:
  Content-Type: application/json
  Accept: application/json
  Authorization: Bearer {{$env.TOKEN}}
  X-Custom-Header: custom-value
```

## Pagination

### Offset-Based
```
Options → Pagination → Offset Based
URL contains: ?offset=0&limit=100
Parameters:
  Limit: 100
  Offset Parameter: offset
  Limit Parameter: limit
Complete when: Response is empty
```

### Cursor/Next URL
```
Options → Pagination → Response Contains Next URL
Next URL Parameter: $.next_url
Complete when: No more pages (next_url is null)
```

### Page Number
```
Options → Pagination → Page Number
Page Parameter: page
Start Page: 1
Page Size: 100
Complete when: Response items < page size
```

### Ручная пагинация (через Loop)
```
1. Set (page=1, hasMore=true)
2. IF (hasMore)
3. HTTP Request (GET /api?page={{$json.page}})
4. Code (проверить hasMore, page++)
5. Loop → назад к шагу 2
```

## Retry & Error Handling

### Встроенный retry
```
Node Settings → On Error:
  ✅ Retry On Fail
  Max Tries: 3
  Wait Between Tries: 1000 (ms)
```

### Continue On Fail
```
Node Settings → On Error → Continue On Fail
// Нода не остановит workflow при ошибке
// Ошибка доступна в output как $json.error
```

### Ручной retry с backoff
```
1. HTTP Request
2. IF ({{$json.statusCode}} !== 200)
3. Wait (exponential: 1s, 2s, 4s, 8s)
4. Set (retryCount + 1)
5. IF (retryCount < maxRetries) → Loop к HTTP Request
6. ELSE → Error Handler
```

### Обработка разных HTTP-кодов
```javascript
// В Code Node после HTTP Request
const statusCode = $json.statusCode || $json.headers?.['status-code'];

switch (true) {
  case statusCode >= 200 && statusCode < 300:
    return [{ json: { success: true, data: $json } }];
  case statusCode === 429:
    return [{ json: { retry: true, reason: 'rate_limit' } }];
  case statusCode >= 500:
    return [{ json: { retry: true, reason: 'server_error' } }];
  default:
    return [{ json: { success: false, error: $json } }];
}
```

## Rate Limiting

### Стратегия 1: Wait Node между запросами
```
Split In Batches (batch size: 1) → HTTP Request → Wait (500ms) → Loop
```

### Стратегия 2: Batch с паузой
```
Split In Batches (batch size: 10) → HTTP Request → Wait (1s) → Loop
```

### Стратегия 3: Throttle через Code
```javascript
const items = $input.all();
const results = [];

for (let i = 0; i < items.length; i++) {
  if (i > 0 && i % 10 === 0) {
    await new Promise(r => setTimeout(r, 1000)); // 1с каждые 10 запросов
  }
  // Обработка...
}

return results;
```

### Обработка 429 (Too Many Requests)
```
HTTP Request → IF (statusCode === 429)
  → Wait (Retry-After header или 60с)
  → HTTP Request (retry)
```

## Обработка ответов

### JSON ответ (по умолчанию)
```javascript
// Данные доступны напрямую
{{$json.data.users[0].name}}
```

### XML ответ
```
Response Format: XML
// n8n автоматически парсит в JSON
```

### Binary (файлы)
```
Response Format: File
// Данные в $binary.data
// Можно передать в Write Binary File или отправить дальше
```

### Full Response (headers + status + body)
```
Options → Full Response: Yes
// $json.statusCode
// $json.headers
// $json.body
```

## Настройки SSL/TLS

### Игнорировать SSL ошибки
```
Options → Allow Unauthorized Certs: Yes
```
Используй для самоподписанных сертификатов (например, VPS-сервисы).

### Client Certificate
```
SSL Certificates → Client Certificate
CA: /path/to/ca.pem
Certificate: /path/to/cert.pem
Key: /path/to/key.pem
```

## Timeout

```
Options → Timeout: 30000 (ms)
```
По умолчанию: 300000 (5 мин). Для быстрых API ставь 10-30 секунд.

## Прокси

```
Options → Proxy: http://proxy.example.com:8080
```

## Частые проблемы

| Проблема | Решение |
|----------|---------|
| CORS ошибка | Не актуально для серверных вызовов (только браузер) |
| SSL certificate error | Allow Unauthorized Certs: Yes |
| Timeout | Увеличить timeout или проверить доступность API |
| 401 после обновления | Обновить credentials/токен |
| Пустой ответ | Проверить Content-Type, Accept headers |
| Данные в неверном формате | Проверить Response Format (JSON/XML/File) |
| Redirect не работает | Options → Follow Redirects: Yes |
| Большой payload обрезается | Увеличить max response size |

## Примеры интеграций с VPS-сервисами

### SearXNG
```
Method: GET
URL: http://<YOUR_VPS_IP>:8888/search
Query Parameters:
  q: {{$json.body.query}}
  format: json
  language: ru
```

### Scraper Server
```
Method: POST
URL: http://<YOUR_VPS_IP>:9111/v0/scrape
Headers:
  Authorization: Bearer <REDACTED>
  Content-Type: application/json
Body:
  {"url": "{{$json.body.url}}"}
```

### Perplexica
```
Method: POST
URL: http://<YOUR_VPS_IP>:3000/api/search
Headers:
  Content-Type: application/json
Body:
  {"query": "{{$json.body.query}}", "focus_mode": "webSearch"}
```

## Чек-лист настройки HTTP Request

- [ ] URL корректный (без лишних пробелов, с протоколом)
- [ ] Метод соответствует API (GET/POST/PUT/DELETE)
- [ ] Аутентификация настроена (credentials, не хардкод)
- [ ] Headers заданы (Content-Type, Accept)
- [ ] Body в правильном формате (JSON/Form/URL-encoded)
- [ ] Timeout адекватный (не слишком маленький)
- [ ] Error handling настроен (retry/continue on fail)
- [ ] Pagination настроена (если API отдаёт постранично)
- [ ] SSL настроен (если self-hosted с самоподписанным cert)
- [ ] Rate limiting учтён (если API ограничивает запросы)
