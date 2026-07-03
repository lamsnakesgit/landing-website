---
name: n8n-validation
description: Интерпретация ошибок валидации n8n, стратегии исправления, профили валидации и auto-sanitization. Используй при ошибках валидации, разборе warnings или перед деплоем workflows.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n Validation Expert

## Философия валидации

**Валидируй рано, валидируй часто.** Валидация — итеративный процесс:
- Ожидай 2-3 цикла validate → fix
- ~23с на анализ ошибок, ~58с на исправление
- Это нормально — не пытайся починить всё за один раз

## Уровни серьёзности

### 🔴 Errors (обязательно исправить)
Блокируют выполнение workflow.

| Тип | Описание | Пример исправления |
|-----|----------|-------------------|
| `missing_required` | Обязательное поле не заполнено | Добавить значение поля |
| `invalid_value` | Значение не из списка допустимых | Использовать допустимое значение |
| `type_mismatch` | Неправильный тип данных | `"100"` → `100` (string → number) |
| `invalid_reference` | Ссылка на несуществующую ноду | Исправить имя ноды |
| `invalid_expression` | Ошибка синтаксиса выражения | Добавить `{{ }}` или исправить путь |

### 🟡 Warnings (желательно исправить)
Не блокируют, но могут вызвать проблемы.

| Тип | Описание |
|-----|----------|
| `best_practice` | Рекомендация (rate limiting, error handling) |
| `deprecated` | Устаревший API/фича |
| `performance` | Потенциальная проблема производительности |

### 🔵 Suggestions (опционально)
Улучшения, не влияющие на работоспособность.

## Профили валидации

| Профиль | Когда использовать | Что проверяет |
|---------|-------------------|---------------|
| `minimal` | Быстрые проверки при редактировании | Только обязательные поля |
| **`runtime`** | **Перед деплоем (рекомендуется)** | **Поля + типы + допустимые значения** |
| `ai-friendly` | AI-генерированные конфигурации | Как runtime, меньше false positives |
| `strict` | Production, критичные workflows | Всё + best practices + безопасность |

## Цикл валидации

```
1. Настроить ноду
   ↓
2. validate_node (профиль: runtime)
   ↓
3. Прочитать ошибки ЦЕЛИКОМ
   ↓
4. Исправить ошибки (по одной)
   ↓
5. validate_node снова
   ↓
6. Повторить до valid (обычно 2-3 итерации)
```

## Частые ошибки и исправления

### missing_required
```javascript
// Ошибка: Channel name is required
// Исправление:
config.channel = "#general";
```

### invalid_value
```javascript
// Ошибка: Operation must be one of: post, update, delete. Current: "send"
// Исправление:
config.operation = "post";
```

### type_mismatch
```javascript
// Ошибка: Expected number, got string. Current: "100"
// Исправление:
config.limit = 100;  // число, не строка
```

### invalid_expression
```javascript
// Ошибка: Invalid expression: $json.name
// Исправление:
config.text = "={{$json.name}}";  // добавить {{ }}
```

### invalid_reference
```javascript
// Ошибка: Node 'HTTP Requets' does not exist
// Исправление: исправить опечатку
config.expression = "={{$node['HTTP Request'].json.data}}";
```

## Auto-Sanitization

Автоматически исправляет структуру операторов при сохранении workflow.

### Бинарные операторы (два значения)
`equals`, `notEquals`, `contains`, `notContains`, `greaterThan`, `lessThan`, `startsWith`, `endsWith`

```javascript
// ❌ До (неправильно)
{ "operation": "equals", "singleValue": true }

// ✅ После (auto-fix)
{ "operation": "equals" }  // singleValue удалён
```

### Унарные операторы (одно значение)
`isEmpty`, `isNotEmpty`, `true`, `false`

```javascript
// ❌ До (неправильно)
{ "operation": "isEmpty" }

// ✅ После (auto-fix)
{ "operation": "isEmpty", "singleValue": true }
```

### Что НЕ исправляется автоматически
- Битые connections (ссылки на несуществующие ноды)
- Несовпадение количества веток Switch и connections
- Коррупция данных API

## Ошибки Workflow (не отдельных нод)

### Битые connections
```
Connection from 'Transform' to 'NonExistent' — target node not found
```
→ Удалить stale connection или создать недостающую ноду.

### Циклические зависимости
```
Circular dependency: Node A → Node B → Node A
```
→ Перестроить workflow, убрать петлю.

### Множественные триггеры
```
Multiple trigger nodes found — only one will execute
```
→ Удалить лишний триггер или разбить на отдельные workflows.

### Отключённые ноды
```
Node 'Transform' is not connected to workflow flow
```
→ Подключить ноду или удалить если не нужна.

## False Positives (ложные срабатывания)

### Когда warning можно проигнорировать

| Warning | Допустимо если... |
|---------|-------------------|
| "Missing error handling" | Простой/тестовый workflow |
| "No retry logic" | API с собственной retry-логикой |
| "Missing rate limiting" | Внутренний API без лимитов |
| "Unbounded query" | Маленький известный датасет |

Для уменьшения false positives используй профиль `ai-friendly`.

## Стратегии восстановления

### 1. Начать заново
Когда конфигурация сильно сломана:
1. Узнать обязательные поля через `get_node`
2. Создать минимальную валидную конфигурацию
3. Добавлять функции инкрементально
4. Валидировать после каждого добавления

### 2. Бинарный поиск
Когда workflow валиден, но работает неправильно:
1. Убрать половину нод
2. Валидировать и протестировать
3. Если работает → проблема в убранных нодах
4. Если нет → проблема в оставшихся
5. Повторить до изоляции проблемы

### 3. Очистка stale connections
```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{ type: "cleanStaleConnections" }]
})
```

### 4. Auto-fix
```javascript
// Предпросмотр исправлений
n8n_autofix_workflow({ id: "workflow-id", applyFixes: false })

// Применить исправления
n8n_autofix_workflow({ id: "workflow-id", applyFixes: true })
```

## Структура ответа валидации

```javascript
{
  "valid": false,           // ← главный флаг
  "errors": [...],          // 🔴 обязательно исправить
  "warnings": [...],        // 🟡 желательно исправить
  "suggestions": [...],     // 🔵 опционально
  "summary": {
    "hasErrors": true,
    "errorCount": 1,
    "warningCount": 1,
    "suggestionCount": 1
  }
}
```

**Порядок действий:**
1. Проверить `valid` → если `true`, всё ОК
2. Исправить `errors` (по одному, с повторной валидацией)
3. Просмотреть `warnings` и решить что исправлять
4. `suggestions` — на усмотрение

## Правила

### ✅ Делай
- Валидируй после каждого значимого изменения
- Читай сообщения об ошибках полностью
- Исправляй ошибки итеративно (по одной)
- Используй профиль `runtime` для пре-деплоя
- Проверяй поле `valid` перед деплоем
- Документируй принятые false positives

### ❌ Не делай
- Не пропускай валидацию перед активацией
- Не чини все ошибки одновременно
- Не используй `strict` при разработке (слишком шумно)
- Не предполагай что валидация пройдена — проверяй result
- Не деплой с неисправленными errors
