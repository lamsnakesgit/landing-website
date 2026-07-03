---
name: n8n-ai-agent-patterns
description: AI Agent workflows в n8n — LangChain ноды, tools, memory, MCP client, fallback routing, structured output. Используй при проектировании AI-агентов или отладке AI workflows в n8n.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# n8n AI Agent Patterns

## Архитектура AI Agent в n8n

```
Trigger → AI Agent
           ├─ ai_languageModel (обязательно)
           ├─ ai_tool (0..N инструментов)
           ├─ ai_memory (0..1 память)
           └─ ai_outputParser (0..1 парсер)
         → Output
```

### Типы подключений (не main, а специальные!)

| Тип подключения | Описание | Пример нод |
|-----------------|----------|------------|
| `ai_languageModel` | LLM-модель | OpenAI, Anthropic, Ollama, Groq |
| `ai_tool` | Инструмент для агента | HTTP Request Tool, Code Tool, Custom |
| `ai_memory` | Память разговора | Window Buffer, Postgres Chat Memory |
| `ai_outputParser` | Парсер ответа | Structured Output, Auto-fixing |

🚨 Эти ноды подключаются **не через main**, а через специальные AI-порты (точки на нижней панели ноды).

## Паттерн 1: Базовый AI Agent

```
Webhook → AI Agent → Webhook Response
           ├─ OpenAI Chat Model
           └─ HTTP Request Tool
```

### Настройка AI Agent ноды
```
Agent Type: Tools Agent (рекомендуется)
System Message: "Ты — помощник. Отвечай кратко и по делу."
Max Iterations: 10
Return Intermediate Steps: No (Yes для отладки)
```

### Настройка LLM
```
OpenAI Chat Model:
  Model: gpt-4o / gpt-4o-mini
  Temperature: 0.7 (креативность) / 0 (точность)
  Max Tokens: 4096

Anthropic Chat Model:
  Model: claude-sonnet-4-20250514
  Temperature: 0.7
  Max Tokens: 4096
```

## Паттерн 2: Agent с Tools

### HTTP Request Tool
```
HTTP Request Tool:
  Name: "search_web"
  Description: "Поиск в интернете по запросу"
  Method: GET
  URL: http://<YOUR_VPS_IP>:8888/search?q={query}&format=json
```

🚨 **Description критически важен!** Агент решает какой tool использовать на основе description.

### Code Tool
```javascript
// Кастомный инструмент через Code
// Input: query (string)
// Output: результат

const query = $json.query;
const response = await $helpers.httpRequest({
  method: 'GET',
  url: `https://api.example.com/search?q=${encodeURIComponent(query)}`
});

return JSON.stringify(response);
```

### Calculator Tool
Встроенный инструмент для математических вычислений.

### Wikipedia Tool
Поиск по Wikipedia — полезен для фактчекинга.

### Workflow Tool (Execute Workflow)
```
Workflow Tool:
  Name: "process_document"
  Description: "Обработать документ и вернуть summary"
  Workflow: [выбрать workflow]
```
Позволяет вызывать другие workflows как инструменты агента.

## Паттерн 3: Agent с Memory

### Window Buffer Memory
```
Window Buffer Memory:
  Context Window Length: 10  // последние 10 сообщений
  Session Key: {{$json.body.session_id}}
```
Для простых чатов. Хранит N последних сообщений в RAM.

### Postgres Chat Memory
```
Postgres Chat Memory:
  Table Name: n8n_chat_histories
  Session ID: {{$json.body.session_id}}
  Connection: [Postgres credential]
```
Для production. Хранит историю в БД, переживает перезагрузки.

### Redis Chat Memory
```
Redis Chat Memory:
  Session Key: chat:{{$json.body.session_id}}
  Session TTL: 3600  // 1 час
```
Быстрая память с автоочисткой.

### Управление сессиями
```javascript
// Генерация session_id из webhook
const sessionId = $json.body.user_id || $json.body.chat_id || crypto.randomUUID();
return [{ json: { ...​$json, sessionId } }];
```

## Паттерн 4: MCP Client в n8n

### Официальный MCP Client Tool
```
MCP Client Tool (для AI Agent):
  Transport: Streamable HTTP / SSE / stdio
  URL: https://mcp-server.example.com
  Authentication: Bearer Token / Header / OAuth2
```

Позволяет AI Agent вызывать **любой MCP-сервер** как инструмент.

### MCP Client Node (для обычного workflow)
```
MCP Client (обычная нода):
  Подключается к MCP-серверу
  Вызывает tools напрямую (без AI Agent)
  Получает resources
```

### Подключение к MCP-серверу
```
Transport: Streamable HTTP
URL: https://your-mcp-server.com/mcp
Headers:
  Authorization: Bearer {{$env.MCP_TOKEN}}
```

## Паттерн 5: Structured Output

### Auto-fixing Output Parser
```
Structured Output Parser:
  JSON Schema: {
    "type": "object",
    "properties": {
      "sentiment": { "type": "string", "enum": ["positive", "negative", "neutral"] },
      "summary": { "type": "string" },
      "score": { "type": "number", "minimum": 0, "maximum": 1 }
    },
    "required": ["sentiment", "summary", "score"]
  }
  Auto-fix: Yes (агент попробует исправить невалидный JSON)
```

### Custom Output через System Prompt
```
System Message:
"Ты анализируешь текст. Всегда отвечай СТРОГО в формате JSON:
{
  "sentiment": "positive|negative|neutral",
  "summary": "краткое описание",
  "keywords": ["ключевое", "слово"]
}
Никакого текста вне JSON."
```

## Паттерн 6: Fallback Routing

### Простой fallback
```
AI Agent → IF (output contains error)
  → True: Fallback Agent (другая модель/промпт)
  → False: Continue
```

### Model fallback
```
1. Try: Claude Sonnet (быстро, дёшево)
2. IF error → Try: GPT-4o (альтернатива)
3. IF error → Return: "Сервис временно недоступен"
```

### Tool fallback
```
AI Agent с tools:
  Tool 1: SearXNG (основной)
  Tool 2: Tavily (fallback если SearXNG не ответил)
```

## Паттерн 7: RAG (Retrieval-Augmented Generation)

```
Query → Vector Store Retriever → AI Agent
          ├─ Embedding Model (OpenAI/Ollama)
          └─ Vector Store (Pinecone/Qdrant/Postgres pgvector)
```

### Индексация документов
```
Document → Text Splitter (chunk_size=1000, overlap=200)
         → Embedding Model → Vector Store (upsert)
```

### Поиск + генерация
```
Query → Embedding → Vector Store (search, top_k=5)
      → AI Agent (context = retrieved chunks)
      → Response
```

## Отладка AI Agent

### Return Intermediate Steps
```
AI Agent → Return Intermediate Steps: Yes
// Показывает каждый вызов tool, каждый reasoning step
```

### Логирование
```javascript
// В Code Node после AI Agent
const output = $json.output;
const steps = $json.intermediateSteps || [];

console.log(`Agent output: ${output}`);
console.log(`Tools used: ${steps.map(s => s.action.tool).join(', ')}`);
console.log(`Total steps: ${steps.length}`);

return [{ json: { output, toolsUsed: steps.length } }];
```

### Частые проблемы

| Проблема | Решение |
|----------|---------|
| Agent зацикливается | Снизить Max Iterations (5-10) |
| Tool не вызывается | Улучшить description tool'а |
| Неправильный tool выбирается | Уточнить description, добавить примеры |
| Медленный ответ | Использовать быструю модель (gpt-4o-mini) |
| Память не работает | Проверить Session ID (должен быть одинаковый) |
| JSON output кривой | Добавить Auto-fixing Output Parser |
| "No tools available" | Проверить подключение tool через AI-порты |
| Rate limit от LLM | Добавить retry + Wait |

## Проверенные рабочие паттерны

### 1. Учебный AI Analyst Chatbot

Успешно подтверждён рабочий учебный паттерн:

**Main workflow:**
```
Chat Trigger → AI Agent
              ├─ Gemini Chat Model
              ├─ Buffer Memory
              ├─ Calculator Tool
              └─ Tool Workflow (sub-workflow)
```

**Sub-workflow:**
```
Execute Workflow Trigger → Code
```

Зачем это полезно:
- можно учить AI Agent без внешней БД;
- tool возвращает структурированный учебный датасет;
- агент умеет и анализировать, и считать;
- memory позволяет держать короткий контекст чата.

### 2. Переиспользование уже рабочих credentials

Если в инстансе уже есть рабочий workflow с моделью, можно переиспользовать credential reference из него.

Проверенный паттерн:
- прочитать существующий workflow через API;
- найти у рабочей LLM-ноды блок `credentials`;
- перенести тот же `credentials` объект в новый workflow.

Это безопаснее, чем гадать имя credential вручную.

### 3. Переключение `System Message` в Expression mode

Успешно подтверждён рабочий рецепт для `AI Agent` ноды:

1. Прочитать workflow через `GET /api/v1/workflows/<workflowId>`
2. Найти `AI Agent.parameters.options.systemMessage`
3. Поставить строку, которая **начинается с `=`**
4. Отправить workflow назад через `PUT /api/v1/workflows/<workflowId>`
5. Проверить новый `versionId`

Пример проверенного формата:

```text
=Ты — учебный AI-аналитик. Отвечай кратко. Текущая дата: {{ $now }}
```

🚨 Ключевое правило: для expression-mode через API нужен именно ведущий символ `=` в значении поля.

## Стоимость и оптимизация

### Выбор модели

| Модель | Скорость | Стоимость | Когда |
|--------|----------|-----------|-------|
| GPT-4o-mini | ⚡⚡⚡ | 💰 | Простые задачи, классификация |
| GPT-4o | ⚡⚡ | 💰💰💰 | Сложный reasoning, code generation |
| Claude Sonnet | ⚡⚡ | 💰💰 | Длинные тексты, анализ |
| Ollama (local) | ⚡ | Бесплатно | Privacy-sensitive, оффлайн |

### Снижение стоимости
- Кэшируй частые запросы (Redis)
- Используй mini-модели для простых задач
- Ограничивай max_tokens
- Фильтруй input до отправки в LLM

## Чек-лист AI Agent Workflow

- [ ] LLM-модель подключена (ai_languageModel порт)
- [ ] System prompt чёткий и конкретный
- [ ] Tools имеют понятные description
- [ ] Memory подключена с правильным Session ID
- [ ] Max Iterations ограничены (5-15)
- [ ] Error handling настроен (fallback)
- [ ] Intermediate Steps включены (для отладки)
- [ ] Temperature подобрана (0 для точности, 0.7 для креатива)
- [ ] Output parser настроен (если нужен JSON)
- [ ] Протестировано с реальными данными
