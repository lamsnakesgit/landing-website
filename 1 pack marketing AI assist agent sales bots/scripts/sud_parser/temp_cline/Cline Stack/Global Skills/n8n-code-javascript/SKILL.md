---
name: n8n-code-javascript
description: Написание JavaScript в n8n Code Node — $input/$json/$node, режимы выполнения, return format, $helpers.httpRequest(), DateTime, типичные ошибки. Используй при написании или отладке JS-кода в n8n.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# JavaScript Code Node в n8n

## Быстрый старт

```javascript
const items = $input.all();

const processed = items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));

return processed;
```

## 5 главных правил

1. Используй режим **"Run Once for All Items"** (95% случаев)
2. Доступ к данным: `$input.all()`, `$input.first()`, `$input.item`
3. 🚨 Возвращай **`[{json: {...}}]`** — массив объектов с ключом `json`
4. 🚨 Webhook-данные под **`$json.body`**, не `$json`
5. Встроенные функции: `$helpers.httpRequest()`, `DateTime` (Luxon), `$jmespath()`

## Выбор режима

### Run Once for All Items (по умолчанию — 95%)
```javascript
const allItems = $input.all();
const total = allItems.reduce((sum, item) => sum + (item.json.amount || 0), 0);

return [{
  json: { total, count: allItems.length, average: total / allItems.length }
}];
```
✅ Агрегация, фильтрация, сортировка, дедупликация, батч-обработка

### Run Once for Each Item (специальные случаи)
```javascript
const item = $input.item;

return [{
  json: { ...item.json, processed: true, processedAt: new Date().toISOString() }
}];
```
✅ Независимый API-вызов на каждый item, per-item валидация

**Не уверен? → Используй "All Items".**

## Доступ к данным

### $input.all() — все элементы (самый частый)
```javascript
const allItems = $input.all();
const valid = allItems.filter(item => item.json.status === 'active');
return valid.map(item => ({ json: { id: item.json.id, name: item.json.name } }));
```

### $input.first() — первый элемент
```javascript
const data = $input.first().json;
return [{ json: { result: data.value * 2 } }];
```

### $node — данные конкретной ноды
```javascript
const webhookData = $node["Webhook"].json;
const httpData = $node["HTTP Request"].json;
return [{ json: { webhook: webhookData, api: httpData } }];
```

## 🚨 Webhook: данные под .body

```javascript
// ❌ НЕПРАВИЛЬНО — вернёт undefined
const name = $json.name;

// ✅ ПРАВИЛЬНО
const name = $json.body.name;
const email = $json.body.email;

// Или через $input
const webhookData = $input.first().json.body;
```

## Формат возврата

```javascript
// ✅ Один результат
return [{ json: { field1: value1, field2: value2 } }];

// ✅ Несколько результатов
return [
  { json: { id: 1, data: 'first' } },
  { json: { id: 2, data: 'second' } }
];

// ✅ Пустой результат
return [];

// ❌ Объект без массива
return { json: { field: value } };

// ❌ Массив без json-обёртки
return [{ field: value }];

// ❌ Без return
const items = $input.all();
// забыл return!
```

## Топ-5 ошибок

### 1. Нет return
```javascript
// ❌ Забыл вернуть данные
const items = $input.all();

// ✅ Всегда возвращай
return items.map(item => ({ json: item.json }));
```

### 2. Выражения n8n в Code Node
```javascript
// ❌ Синтаксис выражений в коде
const value = "{{ $json.field }}";

// ✅ Прямой доступ JavaScript
const value = $input.first().json.field;
```

### 3. Неправильная обёртка return
```javascript
// ❌ Объект вместо массива
return { json: { result: 'success' } };

// ✅ Массив обязателен
return [{ json: { result: 'success' } }];
```

### 4. Нет проверки на null
```javascript
// ❌ Упадёт если user не существует
const value = item.json.user.email;

// ✅ Optional chaining
const value = item.json?.user?.email || 'no-email@example.com';
```

### 5. Webhook без .body
```javascript
// ❌ undefined
const email = $json.email;

// ✅ Правильно
const email = $json.body.email;
```

## Частые паттерны

### Агрегация и отчёты
```javascript
const items = $input.all();
const total = items.reduce((sum, item) => sum + (item.json.amount || 0), 0);

return [{
  json: {
    total,
    count: items.length,
    average: total / items.length,
    timestamp: new Date().toISOString()
  }
}];
```

### Фильтрация и трансформация
```javascript
return $input.all()
  .filter(item => item.json.status === 'active')
  .map(item => ({
    json: {
      id: item.json.id,
      name: item.json.name.toUpperCase(),
      processed: true
    }
  }));
```

### Сортировка и Top N
```javascript
const topItems = $input.all()
  .sort((a, b) => (b.json.score || 0) - (a.json.score || 0))
  .slice(0, 10);

return topItems.map(item => ({ json: item.json }));
```

### Regex и извлечение данных
```javascript
const pattern = /\b([A-Z]{2,5})\b/g;
const matches = {};

for (const item of $input.all()) {
  const found = item.json.text.match(pattern);
  if (found) {
    found.forEach(m => { matches[m] = (matches[m] || 0) + 1; });
  }
}

return [{ json: { matches } }];
```

### Разбиение имени на части
```javascript
return $input.all().map(item => {
  const nameParts = item.json.name.split(' ');
  return {
    json: {
      first_name: nameParts[0],
      last_name: nameParts.slice(1).join(' '),
      email: item.json.email
    }
  };
});
```

## Встроенные функции

### $helpers.httpRequest()
```javascript
try {
  const response = await $helpers.httpRequest({
    method: 'GET',
    url: 'https://api.example.com/data',
    headers: {
      'Authorization': 'Bearer token',
      'Content-Type': 'application/json'
    }
  });
  return [{ json: { success: true, data: response } }];
} catch (error) {
  return [{ json: { success: false, error: error.message } }];
}
```

### DateTime (Luxon)
```javascript
const now = DateTime.now();

return [{
  json: {
    today: now.toFormat('yyyy-MM-dd'),
    iso: now.toISO(),
    tomorrow: now.plus({ days: 1 }).toFormat('yyyy-MM-dd'),
    lastWeek: now.minus({ weeks: 1 }).toFormat('yyyy-MM-dd')
  }
}];
```

### $jmespath()
```javascript
const data = $input.first().json;
const adults = $jmespath(data, 'users[?age >= `18`]');
const names = $jmespath(data, 'users[*].name');

return [{ json: { adults, names } }];
```

## Правила

### ✅ Делай
- Всегда проверяй входные данные на null/undefined
- Оборачивай HTTP-вызовы в try/catch
- Используй `.filter()` перед `.map()` (фильтруй рано)
- Используй описательные имена переменных
- Отлаживай через `console.log()`
- Возвращай пустой массив `[]` если нечего вернуть

### ❌ Не делай
- Не забывай `return`
- Не используй `{{ }}` синтаксис в Code Node
- Не возвращай объект без массива `[...]`
- Не возвращай массив без `{json: ...}` обёртки
- Не обращайся к webhook-данным напрямую (используй `.body`)

## Когда НЕ использовать Code Node

| Задача | Используй вместо Code |
|--------|----------------------|
| Простой маппинг полей | **Set** node |
| Простая фильтрация | **Filter** node |
| Простое условие | **IF** / **Switch** node |
| Только HTTP-запрос | **HTTP Request** node |

**Code Node** отлично подходит для сложной логики, которая потребовала бы цепочку из многих простых нод.

## Чек-лист перед деплоем

- [ ] Код не пустой
- [ ] Есть `return`
- [ ] Формат: `[{json: {...}}]`
- [ ] Доступ к данным: `$input.all()` / `$input.first()` / `$input.item`
- [ ] Нет `{{ }}` синтаксиса
- [ ] Проверки на null/undefined
- [ ] Webhook-данные через `.body`
- [ ] Выбран правильный режим (All Items / Each Item)
- [ ] Все пути кода возвращают одинаковую структуру
