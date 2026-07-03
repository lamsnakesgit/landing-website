---
name: provider-model-testing
description: Техническое тестирование AI-провайдеров и моделей через OpenAI-compatible, OpenAI Responses, Anthropic Messages, Anthropic OpenAI SDK compatibility, Gemini generateContent и совместимые прокси. Используй, когда нужно проверить новый ключ, endpoint, model id, tools, JSON, streaming, usage, latency и цену.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


## 🚀 Quick Start: тестирование НОВОГО провайдера за 15 минут

> **Цель:** быстро понять, что вообще работает у нового провайдера, без фреймворков и библиотек. Только curl + jq.

### Подготовка

```bash
# Установи переменные
export BASE_URL="https://api.new-provider.com/v1"  # или /openai/v1
export API_KEY="<REDACTED>"
export MODEL="model-name-or-id"
```

---

### Шаг 1. Разведка — список моделей (1 мин)

```bash
curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/models" | jq .
```

**Что ищем:**
- ✅ Код 200 и массив моделей → auth рабочий
- ❌ 401 → ключ неверный
- ❌ 404 → endpoint неправиль (может быть `/models` без `/v1/`?)
- ❌ 403 → ключ есть, но нет доступа к endpoint

**Если endpoint `/models` нет** — переходим сразу к Шаг 2, некоторые провайдеры его не дают.

---

### Шаг 2. Basic text — Hello World (2 мин)

```bash
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Reply with exactly OK\"}],
    \"max_tokens\": 10,
    \"temperature\": 0
  }" | jq .
```

**Чек-лист:**
- [ ] Status 200
- [ ] `choices[0].message.content` содержит "OK"
- [ ] `finish_reason` = "stop"
- [ ] `usage` содержит `prompt_tokens` и `completion_tokens`
- [ ] Нет warning или message в ответе

**Если ошибка:**
- 400 bad request → модель не найдена или формат messages неправиль
- 429 → rate limit (попробуй через 30 сек)
- 500 → сервер упал, повторяй позже
- timeout → провайдер медленно отвечает, добавь `--max-time 60`

---

### Шаг 3. JSON output (2 мин)

```bash
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Return exactly this JSON: {\\\"status\\\":\\\"ok\\\"}\"}],
    \"max_tokens\": 64,
    \"temperature\": 0
  }" | jq '.choices[0].message.content'
```

**Что проверяю:**
- [ ] Валидный JSON без markdown-обрамления
- [ ] Нет мусора типа `Here is your JSON:`

Если сломался — добавь `"response_format": {"type": "json_object"}` (работает не у всех).

---

### Шаг 4. Tool calling (3 мин)

```bash
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Compute 5+3 using the calculator tool.\"}],
    \"max_tokens\": 128,
    \"tools\": [{
      \"type\": \"function\",
      \"function\": {
        \"name\": \"calculator\",
        \"description\": \"Calculate math expression\",
        \"parameters\": {
          \"type\": \"object\",
          \"properties\": {
            \"expr\": {\"type\": \"string\"}
          },
          \"required\": [\"expr\"]
        }
      }
    }],
    \"tool_choice\": {\"type\": \"function\", \"function\": {\"name\": \"calculator\"}}
  }" | jq '.choices[0].message.tool_calls // "NO_TOOL_CALLS"'
```

**Что проверяю:**
- [ ] `tool_calls` массив НЕ пустой
- [ ] `function.name` = "calculator"
- [ ] `function.arguments` = `{"expr": "5+3"}`

⚠️ Если модель вернула текст вместо tool_calls — это **неподдерживаемые tools** для этой модели.

---

### Шаг 5. Streaming (2 мин)

```bash
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Say hello\"}],
    \"stream\": true
  }"
```

**Что проверяю:**
- [ ] Ответ начинается сразу (SSE events `data: {...}`)
- [ ] Первый chunk пришёл быстро (TTFT < 3 сек)
- [ ] Поток не обрывается
- [ ] В конце `[DONE]`

---

### Шаг 6. Замер latency (1 мин)

```bash
time curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Count 1 to 5\"}],
    \"max_tokens\": 30
  }" > /dev/null
```

Запиши: **real = X.XXXs**

---

### Результат: таблица

Заполни после всех шагов:

```
Provider:  _________________
Base URL:  _________________
Model:     _________________

┌──────────────────┬────────┬─────────────────────────┐
│ Тест             │ Статус │ Заметка                 │
├──────────────────┼────────┼─────────────────────────┤
│ Auth/Models      │ ✅ / ❌ │                         │
│ Basic text       │ ✅ / ❌ │ Latency: ___ms          │
│ JSON output      │ ✅ / ❌ │ Валидный / грязный      │
│ Tool calling     │ ✅ / ❌ │ tool_calls / текст      │
│ Streaming        │ ✅ / ❌ │ TTFT: ___ms             │
└──────────────────┴────────┴─────────────────────────┘

Цена: $___ / 1M input, $___ / 1M output
Вердикт: Production-ready / Usable / Partial / Unstable / Unsupported
```

---

## 🔑 Anthropic native API — Quick Start (curl)

> Endpoint: `POST https://api.anthropic.com/v1/messages`
> Auth header: `x-api-key: YOUR_KEY` + `anthropic-version: 2023-06-01`

### Anthropic Basic text (1 мин)

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Reply with exactly OK"}]
  }' | jq .
```

**Что проверяю:**
- `content[0].text` = "OK"
- `stop_reason` = "end_turn"
- `usage.input_tokens` / `output_tokens` заполнены

### Anthropic Tool calling

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "Compute 5+3 using the calculator tool."}],
    "tools": [{
      "name": "calculator",
      "description": "Calculate math",
      "input_schema": {
        "type": "object",
        "properties": {"expr": {"type": "string"}},
        "required": ["expr"]
      }
    }]
  }' | jq '.content[] | select(.type == "tool_use")'
```

**Что проверяю:**
- Вернулся block типа `tool_use`
- `name` = "calculator"
- `input` содержит `{expr: "5+3"}`

⚠️ Anthropic возвращает tools через `content[].type=tool_use`, НЕ через `message.tool_calls`.

### Anthropic Streaming

```bash
curl -s -N https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 64,
    "stream": true,
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

**Что проверяю:**
- SSE events: `event: message_start`, `event: content_block_delta`, `event: message_stop`
- Первый chunk пришёл быстро
- `stop_reason` в `message_delta`

---

## 🟢 Gemini native API — Quick Start (curl)

> Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=YOUR_KEY`

### Gemini Basic text (1 мин)

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Reply with exactly OK"}]
    }]
  }' | jq .
```

**Что проверяю:**
- `candidates[0].content.parts[0].text` = "OK"
- `usageMetadata.promptTokenCount` / `candidatesTokenCount` заполнены
- `candidates[0].finishReason` = "STOP"

### Gemini Tool calling (function calling)

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Compute 5+3 using the calculator tool."}]
    }],
    "tools": [{
      "functionDeclarations": [{
        "name": "calculator",
        "description": "Calculate math",
        "parameters": {
          "type": "object",
          "properties": {"expr": {"type": "string"}},
          "required": ["expr"]
        }
      }]
    }],
    "toolConfig": {
      "functionCallingConfig": {"mode": "ANY"}
    }
  }' | jq '.candidates[0].content.parts[] | select(.functionCall)'
```

**Что проверяю:**
- Вернулся `functionCall` block
- `name` = "calculator"
- `args` содержит `{expr: "5+3"}`

⚠️ Gemini использует `functionCall`, НЕ `tool_calls` как OpenAI и НЕ `tool_use` как Anthropic.

### Gemini Streaming

```bash
curl -s -N "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key=$GEMINI_KEY&alt=sse" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Say hello"}]
    }]
  }'
```

**Что проверяю:**
- SSE `data: {...}` events идут
- Ответ начинается сразу (TTFT)
- Нет обрывов

---

## Сводная таблица контрактов

| Фича | OpenAI-compatible | Anthropic native | Gemini native |
|---|---|---|---|
| Endpoint | `/v1/chat/completions` | `/v1/messages` | `/v1beta/models/{m}:generateContent?key=` |
| Auth | `Authorization: Bearer` | `x-api-key` + `anthropic-version` | `?key=` в URL |
| Messages | `messages[].role+content` | `messages[]` (без system!) | `contents[].parts[].text` |
| System prompt | `role: "system"` | top-level `system` | `role: "user"` с инструкцией |
| Tools | `tools[].function` | `tools[].name+input_schema` | `tools[].functionDeclarations` |
| Tool ответ | `message.tool_calls` | `content[].type=tool_use` | `content.parts[].functionCall` |
| Stop reason | `finish_reason` | `stop_reason` | `finishReason` |
| Usage | `usage.prompt_tokens` | `usage.input_tokens` | `usageMetadata` |
| Streaming | `stream: true` → SSE | `stream: true` → SSE | `streamGenerateContent?alt=sse` |
| JSON mode | `response_format.json_object` | Нет (prompt engineering) | Нет (prompt engineering) |

---

# Provider Model Testing

## Routing note

- если задача про **model/provider verification** — visibility, endpoint family, tools, JSON, streaming, latency, usage, price — используй `provider-model-testing`;
- если задача specifically про **`gemini-embedding-2-preview`** как embedding-модель — размерности, multimodal embedding, chunking, retrieval design, provider quirks — после базовой валидации переключайся в skill `gemini-embedding-2-preview`.

---

> Этот skill нужен, когда надо не «просто попробовать запрос», а **системно проверить провайдера, ключ и конкретную модель**: что у неё реально работает, через какой endpoint, в каком JSON-формате, с какими ограничениями и какой фактической задержкой.

Сначала полезно прочитать:
- [`../smoke-test/SKILL.md`](../smoke-test/SKILL.md) — для быстрой базовой проверки после изменений
- [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) — если ответы нестабильны, inconsistent или ошибки плавающие
- [`../../rules/07-tool-usage.md`](../../rules/07-tool-usage.md) — чтобы не объявлять совместимость «подтверждённой» без реального теста

---

## Что это за skill простыми словами

Этот skill помогает проверить 7 вещей:

1. **Ключ вообще рабочий?**
2. **Модель реально видна и доступна?**
3. **Какой endpoint для неё правильный?**
4. **Работают ли text / JSON / tools / search / streaming?**
5. **Какая фактическая latency, usage и форма ответа?**
6. **Какой контракт у модели: OpenAI / Responses / Anthropic / Gemini?**
7. **Как это оформить в нормальный технический отчёт?**

Skill нужен именно для **сравнимых, воспроизводимых и документируемых** тестов, а не для хаотичных одиночных проб.

---

## 📊 Лучшие практики (Best Practices 2025-2026)

### Систематическая оценка (Systematic Evaluation)

> **Ключевой принцип:** AI-модели производят разные выходы на одинаковые входы. Нельзя тестировать AI как детерминированный API.

**Правила:**
- Запускай каждый тест **3-5 раз** для учёта вариативности (кроме temperature=0)
- Измеряй **p50, p90, p99** метрики, а не только среднее
- Используй **детерминированный промпт** с явным ожидаемым ответом ("Reply with exactly OK")
- Фиксируй **seed** если провайдер его поддерживает

### Progressive Testing и A/B сравнение

**Правильный прогресс:**
1. Visibility/Auth → 2. Basic text → 3. JSON → 4. Tools → 5. Streaming → 6. Load test

**A/B тестирование:**
- Запусти одинаковый запрос к нескольким провайдерам одной модели
- Сравни: latency, accuracy, cost, качество JSON
- Используй LLM-as-a-Judge для субъективного сравнения качества

### Мониторинг в production

**Что отслеживать:**
- **TTFT (Time To First Token):** как быстро начинается ответ
- **OTPS (Output Tokens Per Second):** скорость генерации
- **TTCR (Time To Complete Response):** полная задержка
- **Error rate:** частота отказов по типам (429, 500, timeout)
- **Cost per request:** фактическая стоимость на основе usage
- **Token variance:** разница в токенизации между провайдерами

**Важно:** Anthropic токенизирует на 20-30% больше токенов для того же текста, чем OpenAI. Учитывай это при сравнении цен.

### Формирование тестового набора (Test Set)

Создай набор из 10-20 промптов, покрывающих:
- Простые запросы (одно слово/число)
- Средние запросы (объяснение, анализ)
- Сложные запросы (многошаговое рассуждение)
- JSON-запросы (structured output)
- Tool-calling запросы
- Edge cases (длинные тексты, специальные символы)
- Кейсы, где известен правильный ответ

Этот набор становится **ground truth** для последующих сравнений.

### Кэширование и оптимизация

- Semantic caching: ~35% запросов могут быть отвечены из кэша
- Prompt caching: многие провайдеры поддерживают prompt caching (Anthropic: `cache_control`)
- Speculative execution: запускай дешёвую модель параллельно с дорогой для common paths

### Safety и Prompt Injection resilience

- Тестируй на prompt injection: попытка изменить инструкции через пользовательский ввод
- Проверяй policy adherence: соблюдаёт ли модель заданные ограничения
- Bias detection: одинаковое ли поведение при разных входных данных

---

## Когда использовать

- дали новый API key и нужно проверить, что на нём реально работает
- нужно быстро найти рабочий endpoint/контракт для нового proxy или провайдера embeddings/LLM
- появился новый provider / base URL / proxy
- нужно протестировать новую модель или alias
- нужно понять, какой контракт использует модель: OpenAI / Responses / Anthropic / Gemini
- нужно подтвердить tools / JSON / thinking / streaming / search
- нужно сравнить несколько провайдеров одной и той же модели
- нужно привести цены разных провайдеров к **USD per 1M**

## Когда НЕ использовать

- если задача не про верификацию модели, а про обычную интеграцию готового стабильного endpoint
- если уже есть свежий подтверждённый технический отчёт и не требуется повторная валидация
- если нужно просто «быстро спросить модель», а не проверить совместимость

---

## Основной принцип

Тестировать нужно **по лестнице от самого дешёвого и безопасного к самому сложному**.

Никогда не начинай с tools / streaming / long reasoning, если ещё не подтверждены:
- аутентификация
- `GET /models` или эквивалент
- базовый короткий text completion

---

## Универсальная последовательность тестирования

### Этап 0. Подготовка

Перед тестами зафиксируй:
- provider name
- base URL
- model id
- тип ключа / окружение
- заявленные цены
- документацию провайдера
- нативный ли это endpoint или совместимость-слой

Минимум нужно знать заранее:
- где посмотреть список моделей
- какой auth header нужен
- какой JSON-контракт ожидается

---

### Этап 1. Visibility / Auth

Сначала проверь инвентаризацию:

- OpenAI-compatible: `GET /v1/models`
- Anthropic: `GET /v1/models` если поддерживается провайдером, либо сразу `POST /v1/messages`
- Gemini native: часто каталог отдельный не нужен, но если proxy даёт `/v1/models`, используй его

Подтверди:
- ключ валиден
- модель реально присутствует в списке
- если список содержит поле типа `supported_endpoint_types`, зафиксируй его в отчёте

Если модель **не видна**, не переходи к остальным сценариям, пока не зафиксирована причина:
- access denied
- hidden/internal alias
- model not available for this key
- wrong endpoint family

---

### Этап 2. Basic text

Сделай самый короткий запрос, который:
- легко проверить вручную
- не требует длинной генерации
- даёт однозначный expected output

Хорошие тесты:
- `Reply with exactly OK`
- `Return exactly: 255`
- `Ответь только словом: Готово`

Зафиксируй:
- status code
- latency
- model in response
- finish reason / stop reason
- usage / token fields
- реальный текст ответа

Если basic text не работает, tools и JSON проверять рано.

---

### Этап 3. Structured output / JSON

После basic text проверь управляемый формат ответа.

Тестируй:
- короткий JSON-object
- schema / strict JSON, если endpoint это поддерживает

Смотри:
- соблюдается ли JSON без мусора
- не съедают ли reasoning tokens весь лимит
- есть ли `finish_reason=length`
- не требует ли модель больше output budget, чем ожидалось

Важно: у reasoning-моделей JSON часто ломается не из-за схемы, а из-за **слишком маленького output/token budget**.

---

### Этап 4. Tool calling

Только после успешного basic text и/или JSON.

Сначала используй **детерминированный простой tool**:
- calculator
- get_time
- echo

Нужна функция, у которой:
- понятное имя
- простая схема параметров
- один очевидный аргумент

Проверяй:
- модель вообще вернула tool call?
- вернула правильное имя?
- аргументы корректно сериализованы?
- есть ли id / call_id / tool_call_id?
- как выглядит continuation loop после tool result?

Никогда не считай tools подтверждёнными, если модель просто написала текст вроде:
> "I would call calculator with 5+3"

Подтверждение tools = **реальный structured tool/function call в ответе**.

---

### Этап 5. Search / built-in tools

Если провайдер заявляет web search / google search / web_fetch / server-side tools:

- проверь отдельным сценарием
- не смешивай этот тест с первым basic text

Подтверди:
- имя встроенного инструмента
- формат вызова
- приходит ли это как отдельный `tool_call`, `functionCall`, `tool_use`, `server_tool_use` или финальный text+citations

---

### Этап 6. Streaming

Streaming проверяется отдельно от non-stream.

Подтверди:
- есть ли первый chunk
- форма stream событий корректна
- нет ли оборванного JSON / broken SSE / malformed delta
- каков TTFT (time to first token), если это критично

Если provider известен грязным stream или совместимость-слой его ломает — фиксируй это как **contract limitation**, а не просто как «не работает».

---

### Этап 7. Pricing normalization

Все цены в отчёте приводи к одному виду:

- **USD per 1M input tokens**
- **USD per 1M output tokens**

Если провайдер даёт цену в другой валюте:
- фиксируй используемый FX rate
- показывай формулу
- отдельно отмечай, что это пересчёт по текущему курсу, а не официальный долларовый тариф провайдера

Формула:

`price_usd = price_in_local_currency × fx_rate_to_usd`

Например:
- `¥2.0 × 0.1447 = $0.2894`
- `¥12.0 × 0.1447 = $1.7364`

---

## Официальные нюансы по семействам API

## 1. OpenAI-compatible Chat Completions

Обычно endpoint:
- `POST /v1/chat/completions`

Минимальный request:
- `model`
- `messages`
- опционально `max_tokens`, `temperature`, `stream`

Tools:
- `tools[].type = function`
- `tools[].function.name`
- `tools[].function.description`
- `tools[].function.parameters`
- опционально `tool_choice`

Structured output:
- `response_format.type = text | json_object | json_schema`
- для строгого structured output предпочитай `json_schema`

Ожидаемый non-stream ответ:
- `choices[0].message.content`
- либо `choices[0].message.tool_calls`
- `finish_reason`
- `usage.prompt_tokens / completion_tokens / total_tokens`

Практические правила:
- подтверждай tools только по `message.tool_calls`
- подтверждай JSON только если реально парсится output, а не «похоже на JSON»
- отдельно фиксируй `finish_reason=tool_calls`, `stop`, `length`
- если провайдер reasoning-aware, смотри дополнительные usage поля вроде `reasoning_tokens`

### Минимальный шаблон
```json
{
  "model": "MODEL_ID",
  "messages": [
    {"role": "user", "content": "Reply with exactly OK"}
  ],
  "max_tokens": 64,
  "temperature": 0
}
```

### Минимальный tools-шаблон
```json
{
  "model": "MODEL_ID",
  "messages": [
    {"role": "user", "content": "Use the calculator tool to compute 5+3. Do not answer directly."}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "calculator",
        "description": "Calculate a math expression",
        "parameters": {
          "type": "object",
          "properties": {
            "expr": {"type": "string"}
          },
          "required": ["expr"]
        }
      }
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": {"name": "calculator"}
  }
}
```

---

## 2. OpenAI Responses API

Обычно endpoint:
- `POST /v1/responses`

Часто используется для GPT / codex / reasoning-моделей у прокси.

Минимальный request:
- `model`
- `input`
- опционально `max_output_tokens`

Tools часто выглядят иначе, чем в Chat Completions:
- не `messages`, а `input`
- tool result может приходить в `output[]`
- function call и text надо искать в массиве output-блоков

Что обязательно проверять:
- `status`
- `output[]`
- есть ли `type=function_call`
- как выглядит text block
- usage-поля конкретного провайдера

### Минимальный шаблон
```json
{
  "model": "MODEL_ID",
  "input": "Reply with exactly OK",
  "max_output_tokens": 64
}
```

### Минимальный tools-шаблон
```json
{
  "model": "MODEL_ID",
  "input": [
    {"role": "user", "content": "Use the calculator tool to compute 5+3. Do not answer directly."}
  ],
  "tools": [
    {
      "type": "function",
      "name": "calculator",
      "description": "Calculate a math expression",
      "parameters": {
        "type": "object",
        "properties": {
          "expr": {"type": "string"}
        },
        "required": ["expr"]
      }
    }
  ],
  "max_output_tokens": 128
}
```

Не путай `chat/completions` и `responses`: многие прокси поддерживают только один из этих контрактов для конкретной модели.

---

## 3. Anthropic Messages API

Обычно endpoint:
- `POST /v1/messages`

Официальные особенности Anthropic:
- внутри `messages` нет роли `system`; system prompt задаётся **top-level полем `system`**
- `messages[].content` может быть строкой или массивом content blocks
- tools передаются как `tools[].name + description + input_schema`
- при успешном tool use модель возвращает `content[]` block типа `tool_use`
- continuation делается через `user`-message с block типа `tool_result`, где нужен `tool_use_id`

Thinking:
- включается полем `thinking`
- требует минимум **1024 budget_tokens**
- thinking budget учитывается в `max_tokens`
- может возвращать `thinking` block и/или signature

Stop reasons:
- `end_turn`
- `max_tokens`
- `stop_sequence`
- `tool_use`
- `pause_turn`
- `refusal`

Usage:
- `usage.input_tokens`
- `usage.output_tokens`
- могут быть `cache_creation_input_tokens`, `cache_read_input_tokens`
- для server tools есть отдельные usage-поля по tool requests

### Минимальный шаблон
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 256,
  "messages": [
    {"role": "user", "content": "Reply with exactly OK"}
  ]
}
```

### Минимальный tools-шаблон
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 256,
  "messages": [
    {"role": "user", "content": "Use the calculator tool to compute 5+3. Do not answer directly."}
  ],
  "tools": [
    {
      "name": "calculator",
      "description": "Calculate a math expression",
      "input_schema": {
        "type": "object",
        "properties": {
          "expr": {"type": "string"}
        },
        "required": ["expr"]
      }
    }
  ]
}
```

### Минимальный thinking-шаблон
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "thinking": {
    "type": "enabled",
    "budget_tokens": 2048
  },
  "messages": [
    {"role": "user", "content": "Solve this step by step."}
  ]
}
```

Практические правила:
- не пытайся передавать `system` как message role
- не подтверждай tools по тексту; нужен block `tool_use`
- если тестируешь continuation, возвращай `tool_result` с правильным `tool_use_id`

---

## 4. Anthropic Streaming

Anthropic streaming идёт через SSE.

Типовые события:
- `message_start`
- `content_block_start`
- `content_block_delta`
- `content_block_stop`
- `message_delta`
- `message_stop`
- `ping`

При потоковом tool use может идти:
- `input_json_delta`
- fine-grained tool streaming для tool input

В отчёте фиксируй:
- первый event пришёл / нет
- дошёл ли stream до `message_stop`
- есть ли корректный `stop_reason`
- не разваливается ли tool input на грязный partial JSON

---

## 5. Anthropic OpenAI SDK compatibility

Anthropic официально даёт compatibility layer для использования OpenAI SDK.

Но важно:
- это в первую очередь способ **тестировать и сравнивать capabilities**, а не гарантировать полную эквивалентность native Messages API
- при проблемах всегда отдельно проверяй native `/v1/messages`
- если OpenAI facade ломается, а native Anthropic работает — это **важный вывод совместимости**, а не мелочь

Проверяй отдельно:
- работает ли `POST /v1/chat/completions`
- как прокидываются tools
- как прокидывается thinking
- совпадают ли finish_reason / tool calls / usage с ожиданиями

---

## 6. Gemini native API

Обычно endpoint:
- `POST /v1beta/models/{model}:generateContent`

Минимальный request:
- `contents[]`
- `contents[].parts[].text`

Tools:
- `tools[].functionDeclarations[]`
- `toolConfig.functionCallingConfig`

Thinking:
- `generationConfig.thinkingConfig`

Ожидаемый ответ:
- `candidates[]`
- `content.parts[]`
- `functionCall`
- `usageMetadata`
- `thoughtsTokenCount`
- иногда `thoughtSignature`

Для multi-turn tool loop важно:
- вернуть тот же `functionCall.id`
- не потерять thought signatures, если history собирается вручную

### Минимальный шаблон
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {"text": "Reply with exactly OK"}
      ]
    }
  ]
}
```

### Минимальный tools-шаблон
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {"text": "Use the calculator tool to compute 5+3. Do not answer directly."}
      ]
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "calculator",
          "description": "Calculate a math expression",
          "parameters": {
            "type": "object",
            "properties": {
              "expr": {"type": "string"}
            },
            "required": ["expr"]
          }
        }
      ]
    }
  ],
  "toolConfig": {
    "functionCallingConfig": {
      "mode": "ANY",
      "allowedFunctionNames": ["calculator"]
    }
  }
}
```

---

## 7. Gemini через OpenAI-compatible proxy

Многие прокси дают Gemini-модели через:
- `POST /v1/chat/completions`

В этом режиме надо проверить отдельно:
- basic text
- tools как `tool_calls`
- usage fields
- reasoning tokens
- latency относительно native Gemini

Нельзя автоматически считать, что native Gemini и OpenAI facade дадут одинаковое поведение.

---

## Минимальный боевой тест-план

Если времени мало, делай так:

1. **Visibility/Auth**
2. **Basic short text**
3. **JSON / structured output**
4. **Forced calculator tool**
5. **Search/web tool**
6. **Streaming** (если реально нужен)
7. **Pricing normalization to USD**

---

## Что обязательно фиксировать в отчёте

Для каждого теста:
- endpoint
- request payload
- response shape
- status
- latency
- usage
- факт успеха/неуспеха
- отдельное замечание по ограничениям

---

## Output format

Оформляй итог так:

- **Provider:**
- **Base URL:**
- **Auth format:**
- **Model:**
- **Claimed endpoint(s):**
- **Confirmed endpoint(s):**

### Тесты
- **Visibility:** статус, latency, видимость модели
- **Basic text:** статус, latency, ответ, usage
- **JSON:** статус, latency, качество структуры
- **Tools:** статус, latency, имя tool, аргументы, usage
- **Search:** статус, latency, тип вызова
- **Streaming:** работает / не работает / не проверялось

### Pricing
- исходный прайс
- использованный FX rate
- итоговый прайс в USD / 1M

### Вердикт
- **Production-ready / usable / partial / unstable / unsupported**
- что использовать как основной endpoint
- что считать fallback endpoint
- какие ограничения обязательно помнить

---

## Типичные ошибки

- начинать с tools до basic text
- путать `chat/completions` и `responses`
- путать Anthropic native и Anthropic-through-OpenAI facade
- путать Gemini native и Gemini-through-proxy
- объявлять tools working без реального structured tool call
- не фиксировать usage и latency
- писать цену без указания валюты и курса
- не сохранять сырой ответ / артефакты теста
- забывать, что у Anthropic `system` — top-level поле, а не message role
- забывать, что Anthropic thinking съедает budget внутри `max_tokens`

---

## Как проверить, что skill применён правильно

- тесты идут по шагам, а не хаотично
- для каждой capability есть отдельный вывод
- различаются endpoint family и JSON contract
- tools подтверждаются структурно, а не на словах
- отчёт можно передать другому инженеру без дополнительных объяснений

---

## 🔧 Evaluations Frameworks

Когда нужно сравнить модели на конкретном наборе задач, используй фреймворки:

### Встроенные Eval-платформы

| Фреймворк | Когда использовать |
|---|---|
| **LangSmith** | Трассировка LLM, dataset-тестирование, LLM-as-a-Judge |
| **Langfuse** | Experiment-сравнение, cost/latency мониторинг |
| **Braintrust** | CI/CD integration, native SDK для 13+ фреймворков |
| **DeepEval** | Python-фреймворк для юнит-тестирования LLM |
| **Ragas** | Оценка RAG-систем (faithfulness, answer relevance) |
| **Inspect AI** | Multi-provider eval, автоматический выбор `:fastest` / `:cheapest` |

### Типы эвалюаторов

**1. Детерминированные:**
- JSON schema validation
- Regex matching
- Точное сравнение с ожидаемым ответом

**2. LLM-as-a-Judge:**
- Используй стабильную модель-судью (GPT-4o, Claude Sonnet)
- Промпт-судья сравнивает два выхода по критериям
- Недостаток: судья тоже вариативен — запускай 3+ раз

**3. Семантические:**
- Embedding similarity (cosine similarity > 0.85)
- Fact-checking через NLI модели
- Citation accuracy

### CI/CD интеграция

Для production-систем добавь eval в pipeline:

```bash
# Пример: eval на каждый PR с моделью
python run_evals.py --dataset=golden-set --models=gpt-4o,claude-sonnet-4 --threshold=0.85
```

**Автоматические проверки:**
- Accuracy не упала более чем на X% от baseline
- Latency p90 не превышает SLA
- Cost per request в рамках бюджета
- Tool-calling success rate > N%

---

## 📈 Метрики для сравнения провайдеров

### Latency-метрики

| Метрика | Что измеряет | Типичные значения |
|---|---|---|
| **TTFT** | Время до первого токена | 200ms — 3s |
| **OTPS** | Токенов в секунду при генерации | 30 — 650 tokens/s |
| **TTCR** | Полное время ответа | 1s — 30s+ |
| **p50/p90/p99** |_percentile_ задержки | p99 обычно 3-5x p50 |

### Quality-метрики

| Метрика | Что измеряет |
|---|---|
| **Accuracy** | Процент правильных ответов на golden set |
| **Consistency** | Стабильность выходов при повторных запусках |
| **JSON success rate** | Процент валидных JSON ответов |
| **Tool call success rate** | Процент корректных tool calls |
| **Hallucination rate** | Процент выдуманных фактов |

### Cost-метрики

| Метрика | Что измеряет |
|---|---|
| **$/1M input tokens** | Цена ввода |
| **$/1M output tokens** | Цена вывода |
| **Effective cost per query** | Средняя стоимость запроса (с учётом реальных токенов) |
| **Cost per successful answer** | Стоимость с учётом retry и fallback |

**Важные нюансы по ценам:**
- Anthropic токенизирует на 20-30% больше для того же текста
- Reasoning модели: thinking tokens считаются отдельно (Gemini: `thoughtsTokenCount`)
- Streaming vs non-streaming: цена одинакова, но streaming даёт TTFT для UX
- Cache hits: некоторые провайдеры дешевле за cached input (Anthropic: `cache_read_input_tokens`)

---

## ✅ Чек-лист для самопроверки

- [ ] Я проверил visibility/auth отдельно от inference
- [ ] Я подтвердил правильный endpoint, а не только model id
- [ ] Я отдельно протестировал basic text, JSON и tools
- [ ] Я различаю OpenAI / Responses / Anthropic / Gemini контракты
- [ ] Я учитываю official Anthropic nuances: top-level system, tool_use, tool_result, stop_reason, thinking budget
- [ ] Я учитываю official OpenAI nuances: tools, tool_choice, response_format, usage, finish_reason
- [ ] Я сохраняю usage, latency и форму ответа
- [ ] Я привожу цену к USD per 1M
- [ ] Я делаю технический вердикт, а не расплывчатое «вроде работает»
- [ ] Я запускал каждый тест 3-5 раз для учёта вариативности
- [ ] Я записал p50, p90, p99 метрики латентности
- [ ] Я использовал детерминированный промпт с ожидаемым ответом
- [ ] Я протестировал prompt injection resilience
- [ ] Я сравнил цены с учётом tokenization variance между провайдерами
