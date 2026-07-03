# Production patterns for Supabase + Gemini Embedding 2 RAG

## Best-fit improvements for current stack

### 1. Hybrid retrieval
Используй две ветки:
- vector similarity
- weighted full-text search

И затем объединяй результаты через:
- RRF
- или weighted merge

## 2. Metadata-first retrieval
До similarity search фильтруй по:
- course/module/lesson
- access tier
- language
- content_type
- source_id

## 3. Parent-child structure
Для длинных уроков:
- retrieve child chunks
- answer with parent chunks
- хранить matched spans/timecodes

## 4. Reranking layer
Простой production pattern:
- retrieve 20-40
- rerank 20
- answer on 5-8

## 5. Evaluation baseline
Минимум мерить:
- hit@1
- hit@3
- recall@k
- MRR
- latency
- citation precision

## 6. Query transformation
Использовать conditionally:
- query rewrite
- multi-query retrieval
- HyDE for hard queries
