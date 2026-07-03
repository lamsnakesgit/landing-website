# Confirmed workflow and learnings

## Цель документа
Это короткий operational source of truth по **подтверждённому live опыту** работы с official Supabase MCP.

Здесь нет шумной истории ошибок. Только то, что реально сработало и уже было подтверждено живыми вызовами, миграциями, deploy'ем функций и smoke-тестами.

## 1. MCP configuration — что реально работает

### Подтверждённые режимы
#### Safe discovery
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

### Практический порядок переключения
1. Сохранить backup текущего MCP-конфига.
2. Обновить remote URL.
3. Сделать reconnect.
4. Повторно пройти OAuth.
5. Проверить tools живыми вызовами.

## 2. Tools, подтверждённые live
Реально подтверждены:
- `list_tables`
- `list_extensions`
- `execute_sql`
- `apply_migration`
- `list_edge_functions`
- `get_edge_function`
- `deploy_edge_function`
- `get_project_url`

Практический вывод: через official Supabase MCP можно закрывать не только docs lookup, но и реальную operational работу по базе и Edge Functions.

## 3. Edge Functions — подтверждённый workflow

### Что было проверено
- `list_edge_functions` корректно показывает функции проекта.
- Пустой список функций — это валидное состояние, а не ошибка доступа.
- Через MCP успешно задеплоена функция `embed`.
- Функция стала `ACTIVE`.
- Потом функция была live обновлена до версии 2.

### Подтверждённый live паттерн worker
Worker `embed` использовался как internal automation endpoint:
- принимает массив jobs;
- читает данные из Postgres;
- вызывает внешний embeddings provider;
- обновляет vector column обратно в таблицу.

## 4. Vault secrets — подтверждённый workflow

### Что реально использовалось
Для automatic embeddings pipeline были подтверждены такие secret'ы:
- `gemini_embedding_provider_api_key`
- `project_url`

### Практический паттерн
- создавать secret через `vault.create_secret(...)`;
- читать его в SQL или Edge Function через `vault.decrypted_secrets`.

## 5. Pgvector / 3072 dimensions — подтверждённый паттерн

### Что подтверждено
- `extensions.vector(3072)` хранится нормально;
- retrieval можно строить в Supabase;
- HNSW индекс для `3072` dims делается через `halfvec(3072)`.

### Рабочий индекс
```sql
create index ...
on public.my_table
using hnsw (((embedding)::extensions.halfvec(3072)) extensions.halfvec_cosine_ops);
```

## 6. Gemini embeddings E2E через Supabase — что реально подтверждено

Подтверждены live E2E smoke-tests для `gemini-embedding-2-preview`:
- embeddings создаются у внешнего provider;
- сохраняются в Supabase;
- retrieval возвращает правильный chunk как `top1`.

Подтверждённые ключи:
- `1.5Gemini`
- `3Gemini`
- `6Gemini`

Локальные артефакты:
- `cline_docs/rag_e2e_15gemini_result.json`
- `cline_docs/rag_e2e_other_keys_result.json`

## 7. Automatic embeddings pipeline — финальный подтверждённый кейс

### Что было собрано
Для live проекта был собран рабочий pipeline:
- `pgmq`
- `pg_net`
- `pg_cron`
- `hstore`
- `util.project_url()`
- `util.invoke_edge_function()`
- `util.clear_column()`
- `util.queue_embeddings()`
- `util.process_embeddings()`
- queue `embedding_jobs`
- table `public.auto_embed_gemini_docs`
- content function `public.auto_embed_gemini_input`
- retrieval function `public.match_auto_embed_gemini_docs`
- Edge Function worker `embed`
- cron `process-embeddings` every `10 seconds`

### Что подтверждено итоговым smoke-test
Подтверждён сценарий:
1. insert content rows;
2. insert query rows;
3. update content row;
4. queue получает jobs;
5. worker их обрабатывает;
6. embeddings записываются обратно в таблицу;
7. queue в конце становится `0`;
8. retrieval даёт правильный `top1`.

### Финальный подтверждённый результат
- `q_credentials` → top1 = `seg_credentials_n8n_auto`
- `q_chunking` → top1 = `seg_video_chunking_auto`

Локальный артефакт:
- `cline_docs/gemini_auto_embeddings_pipeline_smoke_20260419.json`

## 8. Practical routing
- app integration / SDK / auth / CRUD → `supabase-integration`
- official Supabase MCP / database tools / functions / pgvector / live pipeline → `supabase-mcp`
- model-specific работа по `gemini-embedding-2-preview` → `gemini-embedding-2-preview`
