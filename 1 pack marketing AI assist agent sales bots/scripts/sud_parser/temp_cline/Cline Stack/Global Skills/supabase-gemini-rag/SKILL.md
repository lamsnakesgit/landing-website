---
name: supabase-gemini-rag
description: Используй при проектировании и улучшении production RAG на стеке Supabase + Gemini Embedding 2: hybrid search, metadata filtering, reranking, chunking длинных уроков/видео, parent-child retrieval, evaluation и auto-embeddings pipeline.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Supabase + Gemini Embedding 2 RAG

Коротко: этот skill нужен, когда задача уже не про отдельный embedding endpoint и не про отдельный Supabase MCP, а про **полную retrieval-архитектуру** на связке:
- Supabase / Postgres / pgvector
- Gemini Embedding 2
- Edge Functions / queues / cron
- production retrieval quality

## Когда использовать
- нужно улучшить качество текущего RAG, а не просто заставить его работать;
- нужно добавить hybrid search, reranking, metadata filtering;
- нужно спроектировать chunking для длинных уроков и видео;
- нужно сделать parent-child retrieval;
- нужно определить, какие метрики и eval слой нужны;
- нужно понять, как всё это встроить в Supabase pipeline без лишнего overengineering.

## Когда НЕ использовать
- нужно только проверить endpoint модели → `provider-model-testing`
- нужно только понять `gemini-embedding-2-preview` → `gemini-embedding-2-preview`
- нужно только поднять migrations / Edge Functions / queue → `supabase-mcp`

## Рекомендуемая production architecture

### Stage 0. Ingestion
На входе не хранить «сырой урок одним куском».

Нужны:
- source record
- parent chunk
- child chunk
- metadata table / jsonb metadata
- optional summaries

### Stage 1. Chunking
Для длинных уроков/видео:
- child chunks: 60-90 секунд или короткие смысловые блоки
- overlap: 15-20 секунд
- parent chunk: 3-8 child chunks

### Stage 2. Representation
В embedding string включать:
- title
- lesson/module context
- normalized text
- action summary
- OCR highlights при наличии
- timecode / section cues при необходимости

### Stage 3. Retrieval
Не ограничивайся pure vector search.

Базовый production pattern:
1. metadata filtering
2. vector retrieval top 20-50
3. FTS retrieval top 20-50
4. merge через RRF / weighted merge
5. rerank shortlist
6. collapse child -> parent
7. generation получает top parent blocks + matched spans

## Что именно стоит докрутить в нашем стеке

### 1. Weighted FTS column
В content table или companion table добавить generated/stored `tsvector`.

Что индексировать:
- title — вес A
- short summary — вес A/B
- body/transcript — вес B/C
- OCR/actions — вес C

### 2. Metadata filtering до vector search
Минимальный набор фильтров:
- `course_id`
- `module_id`
- `lesson_id`
- `content_type`
- `access_tier`
- `language`
- `run_id` / `source_id`

### 3. Hybrid merge
Если нет отдельного search service, самый pragmatic вариант:
- SQL function для FTS ranking
- SQL/RPC function для vector ranking
- merge в Edge Function / backend

### 4. Reranking
Рекомендованный pattern:
- retrieve 20-40
- rerank 20
- answer on 5-8

Запускать reranker conditionally:
- long/complex user query
- низкий gap между top results
- retrieval confidence низкий

### 5. Parent-child retrieval
Храни:
- `chunk_id`
- `parent_id`
- `source_id`
- `time_start`
- `time_end`

После retrieval:
- сначала ищи child chunks
- потом группируй по parent
- в answer context отдавай parent text + matching child snippets

## Рекомендованные SQL / data patterns

### Content row
Минимальные поля:
- `id`
- `parent_id` nullable
- `source_id`
- `title`
- `content`
- `summary`
- `metadata jsonb`
- `embedding vector(3072)`
- `fts_weighted tsvector`

### Retrieval functions
Нужны минимум 2 RPC/function слоя:
- vector match function
- FTS ranked function

Опционально 3-й слой:
- hybrid merge function или backend merge layer

## Evaluation layer

### Минимальный набор метрик
- hit@1
- hit@3
- recall@k
- MRR
- latency retrieval
- latency rerank
- answer relevance
- citation precision

### Gold set
Собери dataset из 20-50 кейсов:
- procedural queries
- conceptual queries
- long-video queries
- exact term queries
- ambiguous queries

## Practical roadmap для текущего стека

### Phase 1 — low-risk improvements
- добавить metadata filtering
- добавить weighted FTS
- хранить richer chunk representation
- завести gold set и hit@k metrics

### Phase 2 — higher quality retrieval
- hybrid search merge
- parent-child retrieval
- query rewrite / multi-query для hard queries

### Phase 3 — precision layer
- reranking shortlist
- eval dashboard / regression checks
- conditional retrieval strategies by query type

## Red flags
- не пытаться лечить плохой retrieval только увеличением `top_k`
- не хранить 2-hour lesson одним embedding
- не запускать reranker на всё подряд без budget control
- не смешивать retrieval candidates из разных source scopes без metadata filtering
- не оценивать RAG только по subjective feeling — нужен gold set

## Smoke tests

### Smoke test 1
Запрос:
> Как улучшить текущий vector-only retrieval на Supabase?

Ожидание:
- skill предлагает metadata filtering + FTS + hybrid merge как первый pragmatic step.

### Smoke test 2
Запрос:
> У нас длинные видеоуроки, retrieval плавает. Что менять первым?

Ожидание:
- skill предлагает child/parent chunking, enriched representation, timecodes.

### Smoke test 3
Запрос:
> Как встроить reranking без слишком большого расхода?

Ожидание:
- skill рекомендует rerank только shortlist и conditionally.

### Smoke test 4
Запрос:
> Как понять, что RAG реально улучшился?

Ожидание:
- skill предлагает gold set и retrieval metrics, а не только ручные ощущения.
