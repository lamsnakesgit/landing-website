# Confirmed patterns for gemini-embedding-2-preview

## Что подтверждено live
- Через provider/proxy подтверждён рабочий путь для `gemini-embedding-2-preview`.
- Рабочий OpenAI-compatible endpoint: `POST /v1/embeddings`.
- Рабочий native-family путь тоже подтверждён на этапе исследования: `:embedContent`.
- Все три проверенные ключа (`1.5Gemini`, `3Gemini`, `6Gemini`) успешно прошли live E2E retrieval сценарий.
- Для `3072` dimensions retrieval в Supabase реально работает при индексации через `halfvec(3072)`.
- Query formatting вида `task: question answering | query: ...` показал корректный `top1` retrieval.

## Что использовать по умолчанию
### Для ingestion pipeline
- `POST /v1/embeddings`
- `model = gemini-embedding-2-preview`
- dimensions выбирать по бюджету и storage/profile задачи

### Для Supabase retrieval
- vector column `extensions.vector(3072)` при максимальном качестве
- HNSW index через `halfvec(3072)`
- отдельная retrieval function

## Practical chunking guidance
### Для длинного урока / видео
Начальный рабочий pattern:
- сегменты по `60-90 секунд`
- overlap `15-20 секунд`
- хранить transcript + OCR + actions + screenshot captions

### Для procedural lessons
Собирать компактный enriched chunk:
```text
title: ... | text: ...
```

## Confirmed RAG examples
### Credentials / procedural
```text
title: Настройка API ключа в n8n | text: Открыл Credentials, нажал New, выбрал HTTP Request credential, вставил API key, сохранил. Result: успешная авторизация.
```

### Video chunking / multimodal summary
```text
title: Чанкинг видеоурока | text: Разбил двухчасовой урок на сегменты по 60 секунд с overlap 15 секунд, сохранил transcript, OCR, actions и screenshots для каждого сегмента.
```

### Query example
```text
task: question answering | query: Как разбить двухчасовой урок на сегменты для RAG?
```
