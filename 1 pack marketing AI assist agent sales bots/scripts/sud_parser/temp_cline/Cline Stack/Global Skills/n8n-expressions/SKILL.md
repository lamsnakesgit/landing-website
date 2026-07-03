---
name: n8n-expressions
description: Синтаксис выражений n8n ({{ }}), доступ к $json/$node/$env, работа с webhook-данными и типичные ошибки. Используй при написании или отладке выражений в n8n workflows.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n Expression Syntax

## Формат выражений

Весь динамический контент в n8n использует **двойные фигурные скобки**:

```
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$node["HTTP Request"].json.data}}
❌ $json.email  (без скобок — воспринимается как текст)
❌ {$json.email}  (одинарные скобки — невалидно)
```

## Основные переменные

### $json — данные текущей ноды
```javascript
{{$json.fieldName}}
{{$json['field with spaces']}}
{{$json.nested.property}}
{{$json.items[0].name}}
```

### $node — ссылка на другие ноды
```javascript
{{$node["Node Name"].json.fieldName}}
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```
- Имена нод **в кавычках**, **регистрозависимы**, должны совпадать точно.

### $now — текущая дата/время (Luxon)
```javascript
{{$now}}
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.toFormat('HH:mm:ss')}}
{{$now.plus({days: 7})}}
{{$now.minus({hours: 24}).toISO()}}
```

### $env — переменные окружения
```javascript
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
```

## 🚨 Webhook: данные НЕ в корне!

Самая частая ошибка — webhook-данные обёрнуты в `.body`:

```javascript
// Структура ответа Webhook ноды:
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // ⚠️ Данные пользователя ЗДЕСЬ
    "name": "John",
    "email": "john@example.com"
  }
}

❌ {{$json.name}}
❌ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$json.body.email}}
```

## Частые паттерны

### Вложенные поля и массивы
```javascript
{{$json.user.email}}
{{$json.data[0].name}}
{{$json['field name']}}
{{$json['user data']['first name']}}
```

### Ссылки на другие ноды
```javascript
{{$node["Set"].json.value}}
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```

### Конкатенация
```
Hello {{$json.body.name}}!
https://api.example.com/users/{{$json.body.user_id}}
```

### В свойствах объекта
```json
{
  "name": "={{$json.body.name}}",
  "email": "={{$json.body.email}}"
}
```

## Где НЕ использовать выражения

### ❌ Code Node — прямой JavaScript
```javascript
// ❌ НЕПРАВИЛЬНО в Code Node
const email = '={{$json.email}}';

// ✅ ПРАВИЛЬНО в Code Node
const email = $json.email;
const email = $input.item.json.email;
const allItems = $input.all();
```

### ❌ Webhook Path — только статические пути
### ❌ Credential Fields — используй систему credentials n8n

## Таблица частых ошибок

| Ошибка | Исправление |
|--------|-------------|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `'={{$json.email}}'` (Code) | `$json.email` |

## Работа с типами данных

### Массивы
```javascript
{{$json.users[0].email}}
{{$json.users.length}}
{{$json.users[$json.users.length - 1].name}}
```

### Строки
```javascript
{{$json.email.toLowerCase()}}
{{$json.name.toUpperCase()}}
{{$json.message.replace('old', 'new')}}
{{$json.tags.split(',').join(', ')}}
```

### Числа
```javascript
{{$json.price * 1.1}}   // +10%
{{$json.quantity + 5}}
{{$json.amount.toFixed(2)}}
```

### Условия
```javascript
{{$json.status === 'active' ? 'Активен' : 'Неактивен'}}
{{$json.email || 'no-email@example.com'}}
```

### Даты (Luxon DateTime)
```javascript
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}
{{$now.minus({hours: 24}).toISO()}}
{{DateTime.fromISO('2025-12-25').toFormat('MMMM dd, yyyy')}}
```

## Доступные методы

**String**: `.toLowerCase()`, `.toUpperCase()`, `.trim()`, `.replace()`, `.substring()`, `.split()`, `.includes()`

**Array**: `.length`, `.map()`, `.filter()`, `.find()`, `.join()`, `.slice()`

**DateTime (Luxon)**: `.toFormat()`, `.toISO()`, `.toLocal()`, `.plus()`, `.minus()`, `.set()`

**Number**: `.toFixed()`, `.toString()`, `+`, `-`, `*`, `/`, `%`

## Отладка

1. Открой Expression Editor (кнопка "fx")
2. Смотри live-preview результата
3. Ошибки подсвечиваются красным

**"Cannot read property 'X' of undefined"** → родительский объект не существует, проверь путь.

**Текст показывается как литерал** → забыл `{{ }}`.

## 5 главных правил

1. Всегда оборачивай в `{{ }}`
2. Webhook-данные под `.body`
3. Не используй `{{ }}` в Code Node
4. Имена нод в кавычках: `$node["Имя"]`
5. Имена нод регистрозависимы
