---
name: n8n-workflow-implementation
description: Пошаговая реализация N8N workflows через Public API с проверкой после каждого батча. Используй при создании сложных workflows с множеством нод.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# N8N Workflow Implementation — Best Practices

## Когда использовать
- Создание workflow с 15+ нодами
- Поэтапная реализация сложной логики
- Необходимость проверки после каждого этапа
- Работа через N8N Public API

## Метод батчей (Batch Method)

### Принцип
Разбивай большой workflow на батчи по 5 нод. После каждого батча:
1. PUT — отправить изменения
2. GET — прочитать и проверить
3. Отчитаться о результате

### Размер батча
- **Оптимально:** 5 нод
- **Минимум:** 3 ноды (если сложная логика)
- **Максимум:** 7 нод (если простые ноды)

### Структура батча
```
Batch N:
1. Нода A (тип)
2. Нода B (тип)
3. Нода C (тип)
4. Нода D (тип)
5. Нода E (тип)

Connections:
A → B → C
C (true) → D
C (false) → E
```

## Работа с N8N Public API

### Базовые команды

#### Прочитать workflow
```bash
curl -s -X GET "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <api-key>"
```

#### Обновить workflow
```bash
curl -s -X PUT "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <api-key>" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

#### Проверить после обновления
```bash
curl -s -X GET "https://<n8n-host>/api/v1/workflows/<workflowId>" \
  -H "X-N8N-API-KEY: <api-key>" | jq '{versionId, nodes: (.nodes | length)}'
```

### Паттерн PUT → GET → Verify

**MUST делать после каждого батча:**
```bash
# 1. PUT
curl -s -X PUT ... | jq '{versionId, nodes: (.nodes | length)}'

# 2. GET
curl -s -X GET ... | jq '{versionId, newNodes: [.nodes[-5:] | .[] | .name]}'

# 3. Verify connections
curl -s -X GET ... | jq '.connections["Key Node"]'
```

## Эффективная работа с JSON

### Компактный JSON для экономии контекста
```bash
# Читаем компактно
curl -s ... | jq -c '{name,nodes,connections,settings}' > /tmp/wf.json

# Модифицируем через jq
jq '.nodes += [новые ноды] | .connections["A"] = {...}' /tmp/wf.json

# Отправляем
curl -s -X PUT ... -d @/tmp/wf.json
```

### Добавление нод через jq
```bash
jq '.nodes += [
  {"parameters":{...},"type":"n8n-nodes-base.telegram","position":[x,y],"name":"Node1"},
  {"parameters":{...},"type":"n8n-nodes-base.code","position":[x,y],"name":"Node2"}
]' workflow.json
```

### Обновление connections через jq
```bash
jq '
.connections["Node A"].main[0] = [{"node":"Node B","type":"main","index":0}] |
.connections["Node B"].main[0] = [{"node":"Node C","type":"main","index":0}]
' workflow.json
```

## Типичные ошибки и решения

### Проблема: Connections не работают

**Причина:** Неправильная структура массивов в Switch/If нодах

**Решение:**
```javascript
// ❌ НЕПРАВИЛЬНО
.connections["Switch Node"].main = [{"node":"Target","type":"main","index":0}]

// ✅ ПРАВИЛЬНО
.connections["Switch Node"].main[0] = []  // output 0 пустой
.connections["Switch Node"].main[1] = [{"node":"Target","type":"main","index":0}]
```

### Проблема: Ноды добавились, но не видны

**Причина:** Не указаны credentials или position

**Решение:**
```javascript
{
  "parameters": {...},
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "position": [x, y],  // MUST указать
  "name": "Node Name",
  "credentials": {      // MUST для Telegram/HTTP
    "telegramApi": {
      "id": "credential-id",
      "name": "Bot Name"
    }
  }
}
```

### Проблема: Version ID не меняется

**Причина:** Изменения не применились (ошибка в JSON)

**Решение:**
1. Проверь JSON через `jq .` перед отправкой
2. Проверь что все ноды имеют уникальные имена
3. Проверь что connections ссылаются на существующие ноды

## Проверка connections

### Быстрая проверка всех роутеров
```bash
curl -s -X GET ... | jq -r '
.connections | to_entries | .[] | 
select(.key | IN("Asset Router","Callback Router","Follow-up Router")) | 
"\(.key):\n" + (.value.main | to_entries | map("  [\(.key)] → \(.value[0]?.node // "empty")") | join("\n"))
'
```

### Проверка конкретной ноды
```bash
curl -s -X GET ... | jq '.connections["Node Name"]'
```

## Оптимизация для больших workflows

### Используй jq для модификации вместо чтения в память
```bash
# ❌ Плохо (читает весь JSON в переменную)
WORKFLOW=$(curl -s ...)
echo "$WORKFLOW" | jq ...

# ✅ Хорошо (pipe напрямую)
curl -s ... | jq -c '{name,nodes,connections,settings}' | jq '.nodes += [...]'
```

### Объединяй батчи если контекст позволяет
```bash
# Вместо 3 отдельных PUT для Batch 6-8
# Делай 1 PUT со всеми 12 нодами
jq '.nodes += [batch6_nodes + batch7_nodes + batch8_nodes]'
```

## Структура типичного workflow

### Phase-based organization
```
Phase 1: Foundation (User management)
Phase 2: Configuration (Get settings)
Phase 3: Gate Logic (Subscription check)
Phase 4: Delivery (Send content)
Phase 5: Segmentation (User categorization)
Phase 6: Follow-up (Delayed messages)
Phase 7: Conversion (Final offer)
```

### Naming conventions
- **Ноды:** `Action + Object` (Get User, Send Video, Mark Delivered)
- **Роутеры:** `Type + Router` (Asset Router, Callback Router)
- **Wait ноды:** `Wait + Duration` (Wait 30min, Wait 18h)

## Checklist перед завершением

- [ ] Все ноды имеют connections (кроме финальных)
- [ ] Все Switch/If ноды имеют правильные outputs
- [ ] Все Telegram ноды имеют credentials
- [ ] Все Data Table ноды имеют правильные table IDs
- [ ] Version ID изменился после последнего PUT
- [ ] Проверены ключевые роутеры через GET

## Пример полной реализации

```bash
# Batch 1: User Upsert (5 нод)
curl -s GET ... | jq -c '{name,nodes,connections,settings}' | \
jq '.nodes += [Get User, User Exists?, Create User, Update User, Merge] | 
    .connections["Normalize Event"].main[0] = [{"node":"Get User",...}] | ...' | \
curl -s PUT ... -d @- | jq '{batch:1,versionId,nodes:(.nodes|length)}'

# Проверка
curl -s GET ... | jq '{check:"B1",nodes:(.nodes|length),new:[.nodes[8:13]|.[]|.name]}'

# Batch 2: Config (5 нод)
# ... повторить паттерн
```

---

**Ключевые принципы:**
1. **Батчи по 5 нод** — оптимальный размер
2. **PUT → GET → Verify** — после каждого батча
3. **jq для модификации** — экономия контекста
4. **Проверка connections** — особенно для роутеров
5. **Компактный JSON** — используй `-c` флаг

**Результат:** Стабильная реализация сложных workflows без ошибок и с полной прозрачностью процесса.
