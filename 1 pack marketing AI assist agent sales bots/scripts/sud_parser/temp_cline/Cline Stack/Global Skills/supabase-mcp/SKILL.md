---
name: supabase-mcp
description: Используй при работе с официальным Supabase MCP: remote MCP URL, feature groups, OAuth, database/functions tools, pgvector, Vault, Edge Functions и подтверждённые live workflow для RAG и auto-embeddings.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Supabase MCP

Коротко: этот skill нужен для **операционной работы с официальным Supabase MCP сервером**, когда задача не про SDK в приложении, а именно про:
- подключение и расширение возможностей MCP;
- работу с живым проектом через database/functions tools;
- pgvector / retrieval / Edge Functions;
- автоматизацию embeddings pipeline внутри Supabase.

Ниже собран **только подтверждённый positive/live workflow** без шумной истории ошибок. Это не теоретическая памятка, а рабочая инструкция по тому, что уже реально отработано.

## Когда использовать
- нужно подключить или расширить **официальный Supabase MCP**;
- нужно перейти из `docs-only` режима в `database` или `functions` режим;
- нужно проверить, какие MCP tools реально доступны в текущем проекте;
- нужно работать с `execute_sql`, `apply_migration`, `list_extensions`, `list_edge_functions`, `deploy_edge_function`;
- нужно поднять pgvector retrieval или automatic embeddings pipeline в Supabase;
- нужно сделать live smoke-test для vector search / queue / Edge Function worker.

## Когда НЕ использовать
- задача про обычную интеграцию Supabase SDK в Next.js / Vite / backend;
- задача про frontend auth, CRUD, RLS, Storage без MCP;
- нужен только app-level Supabase client.

Тогда используй:
- `supabase-integration` — для SDK / auth / CRUD / RLS;
- `gemini-embedding-2-preview` — если задача именно про модель Gemini Embedding 2, её размерности, multimodal/RAG паттерны и embedding-стратегию.

## Что подтверждено live

### 1. Рабочие режимы official remote MCP
Подтверждены такие URL-режимы:

#### Безопасный docs-only discovery
```text
https://mcp.supabase.com/mcp?read_only=true&features=docs
```

#### Database + docs
```text
https://mcp.supabase.com/mcp?features=database,docs
```

#### Full features
```text
https://mcp.supabase.com/mcp?features=account,database,debugging,development,functions,storage,branching,docs
```

### 2. После изменения `features` нужен reconnect/OAuth
Подтверждённый live workflow:
1. Сохранить backup MCP-конфига.
2. Обновить remote URL.
3. Переподключить MCP.
4. Повторно пройти OAuth, если клиент его запросил.
5. Проверить tools реальным вызовом.

Практический смысл: не считать новый feature set активным, пока не сделан reconnect + fresh OAuth.

### 3. Реально подтверждённые MCP tools
В live работе подтверждены:
- `list_tables`
- `list_extensions`
- `execute_sql`
- `apply_migration`
- `list_edge_functions`
- `get_edge_function`
- `deploy_edge_function`
- `get_project_url`

Это значит, что через official Supabase MCP уже можно закрывать не только read-only review, но и полноценный workflow:
- DDL / migrations;
- pgvector setup;
- secrets через SQL/Vault;
- deploy/inspect Edge Functions.

## Project ref и project URL

### Как быстро найти `project_ref`
Обычно он виден прямо в project URL:
```text
https://<project-ref>.supabase.co
```

### Как получить API URL через MCP
Подтверждённый вызов:
- `get_project_url(project_id)`

Для live проекта было подтверждено:
```text
https://znojvlfvvhulnrmuqdio.supabase.co
```

Этот URL потом использовался для `project_url` secret в automatic embeddings pipeline.

## Pgvector и retrieval: что реально подтверждено

### Подтверждённое ограничение для 3072 dimensions
Для `vector(3072)` обычный HNSW индекс напрямую не подходит.

Подтверждённый рабочий вариант:
```sql
create index ...
on public.my_table
using hnsw (((embedding)::extensions.halfvec(3072)) extensions.halfvec_cosine_ops);
```

### Практический вывод
Если модель даёт 3072 dims, то в Supabase:
- хранить можно в `extensions.vector(3072)`;
- индекс для retrieval лучше строить через `halfvec(3072)`;
- similarity query должна быть согласована с этим индексным подходом.

## Подтверждённый live RAG workflow через Supabase MCP

### Что было реально сделано
1. Проверили доступность `vector` extension.
2. Создали vector-таблицу и retrieval function.
3. Сгенерировали embeddings вне Supabase через live provider.
4. Записали embeddings в Supabase.
5. Проверили retrieval по query embedding.
6. Подтвердили правильный `top1`.

### Подтверждённый результат
Для `gemini-embedding-2-preview` были успешно проведены live E2E smoke-tests на нескольких ключах провайдера:
- `1.5Gemini`
- `3Gemini`
- `6Gemini`

Подтверждено:
- embeddings создаются;
- записываются в Supabase;
- retrieval возвращает правильный сегмент как `top1`.

Артефакты этой проверки:
- `cline_docs/rag_e2e_15gemini_result.json`
- `cline_docs/rag_e2e_other_keys_result.json`

## Edge Functions через MCP: подтверждённый live workflow

### Как интерпретировать `list_edge_functions`
Если MCP возвращает пустой список функций, это не ошибка доступа. Это означает:
- feature group `functions` подключена;
- tools работают;
- в проекте просто ещё нет deployed functions.

### Что было реально задеплоено
Через MCP успешно задеплоена Edge Function:
- `embed`

Подтверждённые факты:
- slug: `embed`
- status: `ACTIVE`
- `verify_jwt=false`
- потом функция была live обновлена до **version 2**

### Когда оправдан `verify_jwt=false`
Подтверждённый safe case:
- функция вызывается internal automation path'ом через `pg_net` / cron / queue worker;
- это не публичный пользовательский endpoint.

## Vault и secrets: подтверждённый live workflow

### Практический рабочий вариант
Для automatic embeddings worker использовался Supabase Vault.

Подтверждено:
- secret создаётся через `vault.create_secret(...)`;
- worker читает его из `vault.decrypted_secrets`.

Использованный secret name:
```sql
'gemini_embedding_provider_api_key'
```

### Отдельно подтверждено
Для вызова Edge Functions из SQL pipeline использовался ещё и secret:
```sql
'project_url'
```

## Automatic embeddings pipeline: подтверждённый positive/live кейс

### Что было собрано в Supabase
Для live проекта был собран рабочий pipeline со следующими частями:
- `pgmq`
- `pg_net`
- `pg_cron`
- `hstore`
- schema `util`
- helper functions:
  - `util.project_url()`
  - `util.invoke_edge_function()`
  - `util.clear_column()`
  - `util.queue_embeddings()`
  - `util.process_embeddings()`
- queue:
  - `embedding_jobs`
- target table:
  - `public.auto_embed_gemini_docs`
- content function:
  - `public.auto_embed_gemini_input`
- retrieval function:
  - `public.match_auto_embed_gemini_docs`
- cron job:
  - `process-embeddings`
  - schedule: `10 seconds`

### Что было подтверждено live
Подтверждён полный сценарий:
1. insert content rows;
2. trigger отправляет jobs в `embedding_jobs`;
3. cron/process worker вызывает Edge Function `embed`;
4. embeddings записываются обратно в таблицу;
5. query rows тоже получают embeddings;
6. retrieval возвращает правильный `top1`.

### Важный live-урок, который уже учтён в рабочем варианте
Чтобы pipeline был действительно устойчивым, в worker `embed` должны быть:
- удаление job из `pgmq` после успешной обработки;
- retry на `429` / `5xx` со стороны внешнего provider.

Это уже подтверждено и внесено в рабочую live-версию worker.

### Артефакт финального smoke-test
Сохранён локально:
- `cline_docs/gemini_auto_embeddings_pipeline_smoke_20260419.json`

Там зафиксировано:
- какой pipeline поднят;
- какой worker задеплоен;
- какой `test_run` использовался;
- что queue после прогона стала `0`;
- что retrieval дал правильный `top1` для обоих запросов.

## Пошаговый live workflow: как повторять

### Сценарий A — включить MCP и проверить database/functions tools
1. Поставить нужный remote URL с корректными `features`.
2. Сделать reconnect.
3. Повторно пройти OAuth.
4. Вызвать:
   - `list_extensions`
   - `list_tables`
   - `list_edge_functions`
5. Только после этого переходить к migrations/functions workflow.

### Сценарий B — поднять pgvector retrieval под 3072 dims
1. Проверить `vector` extension.
2. Создать таблицу с `extensions.vector(3072)`.
3. Создать HNSW index через `halfvec(3072)`.
4. Создать retrieval function.
5. Записать test embeddings.
6. Проверить similarity query на `top1`.

### Сценарий C — поднять automatic embeddings pipeline
1. Включить extensions:
   - `vector`
   - `pgmq`
   - `pg_net`
   - `pg_cron`
   - `hstore`
2. Создать `util` schema и helper functions.
3. Создать queue `embedding_jobs`.
4. Создать target table + content function + retrieval function.
5. Настроить insert/update triggers.
6. Создать secret'ы в Vault.
7. Задеплоить Edge Function worker `embed`.
8. Создать cron schedule.
9. Прогнать smoke-test insert/update/query -> embeddings -> retrieval.

## Что НЕ нужно путать
- Supabase MCP ≠ обычный Supabase SDK workflow.
- `pgvector` ≠ генерация embeddings.
- empty `functions: []` ≠ ошибка access.
- full feature URL без reconnect/OAuth ≠ реально активные tools.

## Practical smoke tests

### Smoke test 1
Запрос:
> Включи database+docs режим и проверь, что database tools реально появились.

Ожидаемое поведение:
- skill обновляет MCP URL;
- напоминает про reconnect/OAuth;
- проверяет `list_extensions` / `list_tables`.

### Smoke test 2
Запрос:
> Проверь, доступны ли через MCP Edge Functions tools и можно ли задеплоить worker.

Ожидаемое поведение:
- skill зовёт `list_edge_functions`;
- корректно интерпретирует пустой список;
- дальше использует `deploy_edge_function`.

### Smoke test 3
Запрос:
> Подними live automatic embeddings pipeline в Supabase под Gemini.

Ожидаемое поведение:
- skill включает нужные extensions;
- создаёт util/schema/queue/triggers/cron;
- деплоит `embed` worker;
- прогоняет insert/update/query smoke-test до retrieval.

## Routing note
- обычная app integration → `supabase-integration`
- official Supabase MCP / project operations / pgvector / Edge Functions / automatic embeddings → `supabase-mcp`
- если задача specifically про модель `gemini-embedding-2-preview`, её размерности, multimodal chunking, Embedding 2 task-format и RAG design → `gemini-embedding-2-preview`
- если задача про полный production RAG-паттерн на связке Supabase + Gemini Embedding 2 (hybrid search, reranking, metadata filtering, evaluation, parent-child chunking) → `supabase-gemini-rag`
