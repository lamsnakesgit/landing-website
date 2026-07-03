---
name: langsmith-fetch
description: Интеграция с LangSmith для трассировки, мониторинга и оценки качества работы LLM.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# LangSmith Fetch Skill

## Настройка окружения
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="your-api-key"
export LANGCHAIN_PROJECT="my-project"
```

**Best practice:** Используй отдельные проекты для dev/staging/prod через `LANGCHAIN_PROJECT`.

## Трассировка (Tracing)

### Базовое использование
```python
from langsmith import traceable
import openai

client = openai.Client()

@traceable(run_type="llm", name="OpenAI Call")
def call_llm(prompt: str):
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
```

### Метаданные и теги
Добавляй контекст для фильтрации в UI:
```python
@traceable(
    metadata={"version": "v2", "model": "gpt-4"},
    tags=["prod", "user-facing"]
)
def process_query(query: str):
    ...
```

### Вложенные трейсы
Для цепочек вызовов — child spans создаются автоматически:
```python
@traceable(name="Full Pipeline")
def pipeline(query: str):
    context = retrieve_docs(query)   # Автоматический child span
    answer = generate_answer(context) # Автоматический child span
    return answer

@traceable(name="Retrieve Docs")
def retrieve_docs(query: str):
    ...

@traceable(name="Generate Answer")
def generate_answer(context: str):
    ...
```

## Оценка (Evaluation)

### Создание Dataset
```python
from langsmith import Client

client = Client()

dataset = client.create_dataset("my-qa-dataset")
client.create_examples(
    inputs=[
        {"question": "Что такое RAG?"},
        {"question": "Как работает embedding?"},
    ],
    outputs=[
        {"answer": "Retrieval-Augmented Generation..."},
        {"answer": "Embedding преобразует текст в вектор..."},
    ],
    dataset_id=dataset.id
)
```

### Запуск оценки
```python
from langsmith.evaluation import evaluate

results = evaluate(
    my_llm_function,
    data="my-qa-dataset",
    evaluators=[
        "correctness",
        "relevance",
        "coherence",
    ],
    experiment_prefix="v2-gpt4",
)
```

### Кастомные оценщики
```python
def check_contains_keyword(run, example):
    prediction = run.outputs.get("answer", "")
    expected_keywords = example.outputs.get("keywords", [])
    score = all(kw in prediction for kw in expected_keywords)
    return {"key": "keyword_match", "score": score}
```

## Мониторинг

### Что отслеживать
- **Latency**: Время ответа LLM (p50, p95, p99).
- **Token Usage**: Потребление токенов и стоимость.
- **Error Rate**: Процент ошибок (timeouts, rate limits).
- **Feedback Score**: Оценки от пользователей.

### Feedback Loops
```python
from langsmith import Client

client = Client()

# Записать обратную связь
client.create_feedback(
    run_id="run-uuid-here",
    key="user-rating",
    score=1.0,  # 0.0 - 1.0
    comment="Отличный ответ"
)
```

## Prompt Versioning
- Используй LangSmith Hub для хранения и версионирования промптов.
- Сравнивай версии через A/B тестирование в Playground.
- Связывай промпт-версию с экспериментом через `experiment_prefix`.

## Лучшие практики
- 🚨 Всегда трассируй продакшен-вызовы (overhead минимальный).
- Используй `tags` для A/B тестов: `tags=["prompt-v1"]` vs `tags=["prompt-v2"]`.
- Создавай datasets из реальных пользовательских запросов.
- Настрой алерты на аномалии (рост latency, падение quality scores).
- Регулярно проводи offline evaluation перед деплоем новых промптов.
