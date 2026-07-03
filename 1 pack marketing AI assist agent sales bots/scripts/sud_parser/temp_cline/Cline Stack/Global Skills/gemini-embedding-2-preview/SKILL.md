---
name: gemini-embedding-2-preview
description: Используй при работе с `gemini-embedding-2-preview`: выбор endpoint, размерности 768/1536/3072, task formatting, multimodal limits, chunking длинных уроков, retrieval design и практический workflow для RAG/auto-embeddings.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Gemini Embedding 2 Preview

Коротко: этот skill нужен, когда задача не просто «получить embedding», а **системно использовать `gemini-embedding-2-preview` в боевом retrieval / RAG / ingestion pipeline**.

Он покрывает:
- какой endpoint использовать;
- как задавать размерность;
- как оформлять text/query input;
- когда модель подходит для multimodal embedding;
- как проектировать chunking длинных уроков и видео;
- как использовать модель в связке с Supabase / pgvector / Edge Functions.

## Когда использовать
- нужно разобраться именно с моделью `gemini-embedding-2-preview`;
- нужно выбрать между `768`, `1536`, `3072` dimensions;
- нужно построить retrieval / RAG / semantic search на Gemini embeddings;
- нужно проектировать chunking для длинных уроков, транскриптов, PDF, multimodal данных;
- нужно понять, как безопасно использовать модель через proxy/provider;
- нужно спроектировать auto-embedding pipeline или ingestion workflow.

## Когда НЕ использовать
- нужно просто проверить, рабочий ли новый provider endpoint — сначала используй `provider-model-testing`;
- задача только про Supabase MCP / migrations / Edge Functions tools — используй `supabase-mcp`;
- задача про обычную app integration с Supabase SDK — используй `supabase-integration`.

## Что подтверждено live

### 1. Рабочие endpoint family
Для `gemini-embedding-2-preview` подтверждены два реально рабочих подхода:

#### OpenAI-compatible embeddings endpoint
```text
POST /v1/embeddings
```

#### Gemini-native endpoint
```text
POST /v1beta/models/gemini-embedding-2-preview:embedContent
```

Практический вывод:
- если provider/proxy даёт нормальный OpenAI-compatible слой, можно использовать `POST /v1/embeddings`;
- если нужен first-party/native контракт — используй `embedContent`.

### 2. Подтверждённые размерности
Для модели подтверждены рабочие размерности:
- `768`
- `1536`
- `3072`

Практический выбор:
- `768` — когда важнее скорость, стоимость и компактность;
- `1536` — хороший компромисс по качеству/размеру;
- `3072` — максимальная полнота сигнала для retrieval, если storage/index budget позволяет.

### 3. Подтверждённый live E2E через provider keys
На практике были подтверждены три рабочих ключа одного provider path:
- `1.5Gemini`
- `3Gemini`
- `6Gemini`

Для всех трёх подтверждено:
- embeddings создаются;
- embeddings пишутся в Supabase;
- retrieval возвращает правильный `top1`.

## Practical model contract

### OpenAI-compatible request
Минимальный shape:
```json
{
  "model": "gemini-embedding-2-preview",
  "input": "text to embed"
}
```

### Gemini-native request
Минимальный shape:
```json
{
  "content": {
    "parts": [
      {"text": "text to embed"}
    ]
  }
}
```

### Практический совет
Если задача — production ingestion pipeline через proxy, обычно проще и быстрее жить на `POST /v1/embeddings`, потому что:
- проще контракт;
- легче интеграция с существующим RAG tooling;
- проще сменить provider без полной переработки слоя embeddings.

## Task formatting и retrieval semantics

### Что реально работает лучше
Для query side полезно задавать явный retrieval intent в тексте запроса.

Подтверждённый практический паттерн:
```text
task: question answering | query: Как он в уроке настраивал credentials в n8n?
```

Такой формат уже использовался в live smoke-тестах и дал корректный retrieval.

### Практический вывод
Для production лучше разделять хотя бы два типа input:
- document/content embedding;
- query embedding.

Минимальный pragmatic pattern:
- content: нормализованный текст сегмента;
- query: краткий вопрос с retrieval intent prefix.

## Multimodal и ограничения модели

### Что важно помнить
`gemini-embedding-2-preview` — не просто text-only модель. Она может работать шире, но для production retrieval надо проектировать ingestion осознанно.

Подтверждённые практические ориентиры, которые использовались в исследовании:
- text limits порядка `8192` tokens;
- для мультимодальных source-данных нужны предварительная нормализация и extraction layer;
- длинные видео и уроки не стоит пытаться embed'ить «одним куском».

### Практический принцип
Для длинных уроков / видео embedding нужно строить не от «сырого длинного объекта», а от **подготовленных смысловых сегментов**.

## Chunking длинных уроков и двухчасовых видео

### Что работает практически
Для длинного обучающего видео/урока хороший production pattern такой:
1. Разбить материал на короткие сегменты.
2. Для каждого сегмента собрать нормализованный текст.
3. В текст сегмента включать не только transcript, но и полезный retrieval context.

### Рекомендуемая структура сегмента
Для каждого chunk хранить:
- `transcript`
- `OCR`
- `actions`
- `screenshot captions`
- служебную metadata: lesson/module/time-range/topic

### Подтверждённый live chunking example
Один из live сегментов, который корректно находился retrieval'ом:
```text
title: Чанкинг видеоурока | text: Разбил двухчасовой урок на сегменты по 60 секунд с overlap 15 секунд, сохранил transcript, OCR, actions и screenshots для каждого сегмента.
```

### Практический выбор размера chunk
- для procedural/tutorial content — короткие смысловые куски;
- для видео — начни с `60-90 секунд` + overlap;
- если retrieval промахивается, сначала улучшай representation чанка, а не сразу увеличивай размерность.

## Рекомендуемая retrieval architecture

### Minimal production pattern
1. Preprocess source.
2. Собрать `content string` для каждого chunk.
3. Сгенерировать embeddings.
4. Хранить embeddings в vector DB.
5. Для запроса делать отдельный query embedding.
6. Возвращать top-k chunks.
7. Потом уже передавать их в generation layer.

### Для Supabase / pgvector
Если используешь `3072` dims:
- vector column: `extensions.vector(3072)`;
- index: через `halfvec(3072)`;
- retrieval function — отдельная SQL/RPC function.

## Auto-embeddings pipeline pattern

### Подтверждённый practical pattern
Для Gemini Embedding 2 уже подтверждён рабочий pipeline вида:
- insert/update source row;
- queue job;
- Edge Function worker `embed`;
- вызов provider `POST /v1/embeddings`;
- запись embedding обратно в таблицу;
- retrieval query по той же таблице.

### Что важно в worker
Для устойчивой работы worker должен:
- уметь читать secret провайдера безопасно;
- удалять job из queue после успеха;
- делать retry на `429/5xx`.

## Provider / proxy best practice

### Если работаешь через proxy
Подтверждённый safe workflow такой:
1. Проверить `/models` или visibility через provider.
2. Подтвердить, что модель реально доступна по ключу.
3. Протестировать basic embedding request.
4. Только потом подключать модель в Supabase pipeline.

### Почему это важно
Если сразу строить pipeline без provider verification, потом трудно отделить:
- проблему модели;
- проблему proxy;
- проблему Supabase pipeline;
- проблему очереди/worker.

## Готовые practical examples

### Example 1 — procedural content chunk
```text
title: Настройка API ключа в n8n | text: Открыл Credentials, нажал New, выбрал HTTP Request credential, вставил API key, сохранил. Result: успешная авторизация.
```

### Example 2 — chunking/video chunk
```text
title: Чанкинг видеоурока | text: Разбил двухчасовой урок на сегменты по 60 секунд с overlap 15 секунд, сохранил transcript, OCR, actions и screenshots для каждого сегмента.
```

### Example 3 — query embedding text
```text
task: question answering | query: Как разбить двухчасовой урок на сегменты для RAG?
```

## Smoke tests

### Smoke test 1 — endpoint confirmation
Запрос:
> Найди рабочий endpoint для `gemini-embedding-2-preview` у нового provider.

Ожидаемое поведение:
- skill проверяет OpenAI-compatible и native варианты;
- подтверждает реальный рабочий endpoint;
- фиксирует payload shape.

### Smoke test 2 — dimension choice
Запрос:
> Под какую размерность лучше запускать RAG: 768, 1536 или 3072?

Ожидаемое поведение:
- skill объясняет trade-offs;
- рекомендует размерность под конкретный retrieval/storage budget.

### Smoke test 3 — long lesson chunking
Запрос:
> Как лучше разложить двухчасовой урок под Gemini Embedding 2?

Ожидаемое поведение:
- skill предлагает segment-based ingestion;
- объясняет, что хранить в chunk representation;
- даёт practical size/overlap starting point.

### Smoke test 4 — Supabase auto-embeddings
Запрос:
> Хочу automatic embeddings pipeline в Supabase именно под Gemini Embedding 2.

Ожидаемое поведение:
- skill проектирует queue/worker/retrieval pattern;
- рекомендует Edge Function worker + provider verification;
- при необходимости маршрутизирует operational часть в `supabase-mcp`.

## Routing note
- provider/endpoint verification → `provider-model-testing`
- Supabase MCP / migrations / Edge Functions / queue / cron → `supabase-mcp`
- model-specific design и паттерны `gemini-embedding-2-preview` → `gemini-embedding-2-preview`


## Как докрутить качество RAG

Ниже не абстрактные советы, а production-паттерны, которые хорошо ложатся на стек **Supabase + Gemini Embedding 2**.

### 1. Hybrid search вместо pure vector-only
Если в данных встречаются:
- точные термины;
- названия модулей;
- SKU/ID/имена инструментов;
- новые product names;
то одного semantic search недостаточно.

Практический паттерн:
- stage 1A: vector retrieval по embeddings;
- stage 1B: Postgres FTS / weighted tsvector;
- merge: reciprocal rank fusion (RRF) или простой weighted merge;
- stage 2: reranking top-N.

Для нашего стека это значит:
- embeddings храним в `vector`;
- keyword слой строим на `tsvector` generated column + GIN index;
- final shortlist собираем уже после merge двух списков.

### 2. Metadata filtering как обязательный слой
До reranking и generation полезно фильтровать по:
- `course_id`
- `module_id`
- `lesson_id`
- `content_type`
- `language`
- `access_tier`
- `time_range` / `segment_type`

Практический смысл: retrieval должен сначала сузить область поиска, а уже потом сравнивать embeddings.

### 3. Reranking как второй stage
Для production качества полезный паттерн:
- retrieve top 20-50
- rerank top 20
- в generation отдавать top 5-8

Что rerank'ить:
- query vs chunk text
- query vs short normalized summary chunk

Если compute budget ограничен, reranker можно запускать только:
- для длинных вопросов;
- для low-confidence retrieval;
- когда top-k слишком близки по distance.

### 4. Parent-child retrieval
Для длинных уроков и видео полезно хранить два уровня:
- child chunks: короткие retrieval units
- parent chunks: более крупные блоки для final context

Практический flow:
1. embed child chunks
2. retrieve child chunks
3. collapse по `parent_id`
4. в generation отдавать parent context + matched child spans

### 5. Chunk enrichment
Chunk должен содержать не только transcript.

Минимально полезно добавлять:
- title
- section / lesson name
- key action summary
- OCR highlights
- timecode markers
- modality tags

### 6. Evaluation слой
Для нашего стека стоит мерить хотя бы:
- hit@1
- hit@3
- MRR
- recall@k
- answer relevance
- citation precision
- latency retrieval / rerank / full answer

Минимальный gold set:
- 20-50 query->expected chunk кейсов
- отдельно procedural questions
- отдельно conceptual questions
- отдельно long-video queries

### 7. Query transformation
Когда вопрос слишком короткий или ambiguous, полезны:
- query rewrite
- multi-query retrieval
- HyDE / synthetic answer draft

Но запускать это нужно не всегда, а только conditionally:
- low confidence retrieval
- short vague query
- no good hit in top-k

### 8. Нормализация similarity слоя
Если embeddings нормализованы, можно использовать:
- cosine
- inner product

Практически для speed часто удобен inner product / cosine-consistent retrieval при согласованной индексации.

## Routing note
- provider/endpoint verification → `provider-model-testing`
- Supabase MCP / migrations / Edge Functions / queue / cron → `supabase-mcp`
- production RAG architecture на связке Supabase + Gemini Embedding 2 → `supabase-gemini-rag`
- model-specific design и паттерны `gemini-embedding-2-preview` → `gemini-embedding-2-preview`
