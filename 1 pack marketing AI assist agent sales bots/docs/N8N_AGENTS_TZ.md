# ТЗ: Ремонт и проектирование AI-агентов N8N

## 1. Короткий вывод

Сейчас у нас есть рабочий, но плохо структурированный набор воркфлоу. Задача — не выдумывать всё с нуля, а починить то, что сломано, и явно описать архитектуру, чтобы следующий агент не угадывал.

## 2. Что уже работает

- Главный воркфлоу `00 - ГЛАВНЫЙ + GOOGLE Ассистент ЛИЧНЫЙ Pod` поддерживает:
  - текст, голос, фото, документы, видео
  - подключение внешних инструментов: Calendar, Image Generation, Search, Suno
  - fallback-модели через OpenRouter + GRSAI
  - Postgres Chat Memory для долгой памяти
- Unified Assistant Agent — упрощённый единый агент с теми же инструментами, но в 17 нодах.

## 3. Что сломано/непонятно

### 3.1. Главный воркфлоу
- **204 ноды + 116 connections.** Сложность зашкаливает.
  - Дублирующиеся ноды: 3x `GoogleGeminiChatModel` + 3x `OpenaiChatModel` + несколько `lmChatOpenAi` с похожими кредами.
  - Неясно, почему 3 ассистента (`MainAgent`, `AiAgent`, `MainAgent1`) вместо одного.
  - Code/CleanText/ChunkSplitter/SplitInBatches встречаются по 2-3 раза — возможно одна и та же логика.
- **Agent Loop слишком сложный.** Выходы `.out(1)` идут вверх по конвейеру без чёткого контракта.
  - Фактически это `OR` ветки: либо TTS, либо текстовый ответ, либо повторный вызов агента.
- **Непонятно, что делает `ModelSelector`.** В `Unified_Assistant_Agent` он пустой. В главном воркфлоу висит `ModelSelector1` без явного назначения.
- **Текстовая генерация и TTS на одной линии.** Сейчас LLM отвечает → текст чистится → дробятся чанки → каждый чанк в TTS → аудио отправляется. Это медленно и ненадёжно.
- **Генерация изображений.** `GenerateAnImageInGoogleGemini` и `CreateImage` (N8N tool-workflow) — непонятно какая из них живая, какая дубль.
- **Поиск.** `SearchInTavily` и `InternetDeepSearch` — непонятно когда что вызывается.

### 3.2. Unified Assistant Agent
- `active: false` — не включён, не понятно запускается ли он вообще.
- `ModelSelector` пустой.
- `GenerateImageTool` использует `gemini-2.5-flash-lite` — устаревшая/неудачная модель (по логам плохо генерирует кириллицу).
- Нет явного лимита `maxIterations` в агенте (в главном есть `maxIterations: 30`).
- Нет явного error output для `MainAgent` — в неудачном сценарии пользователь не получит ответ.

## 4. Что нужно сделать — план работ

### Этап 1. Аудит и консолидация моделей
- [ ] Оставить **один** primary LLM узел на воркфлоу, а не 6 штук.
- [ ] Использовать `vertex_sa.json` для Vertex AI, когда модель требует `global` endpoint (`gemini-3.1-flash-image`).
- [ ] Для текстовых моделей использовать openrouter/grsai как fallback: `gpt-4o-mini` через AIHubMix + OpenRouter free models.
- [ ] Удалить дублирующиеся `GoogleGeminiChatModel` 1-6 и завести `PrimaryLLM` + `FallbackLLM`.
- [ ] `ModelSelector` и `ModelSelector1` — объявить явно, что выбирают.

### Этап 2. Упрощение Agent Loop
- [ ] Сделать **один** MainAgent с `maxIterations: 15` и явным `onError → SendErrorMessage`.
- [ ] Убрать `AiAgent` и `MainAgent1` как отдельные сущности, если они дублируют MainAgent.
- [ ] Concurrency: если агент генерирует TTS и картинку одновременно — запускать параллельно, а не последовательно.
- [ ] `SendChatAction` (печатает/записывает) — вынести в Pre-execution hook, а не через отдельные ноды.

### Этап 3. Исправление генерации медиа
#### Изображения
- [ ] Создать **один** узел `GenerateImage` на `gemini-3.1-flash-image` (Nano Banana 2) через `global` endpoint.
- [ ] Удалить дубли `CreateImage` и `GenerateAnImageInGoogleGemini` — оставить один tool-call.
- [ ] Добавить fallback: если Vertex не доступен, использовать `imagen-3.0-generate-002` через REST.

#### Аудио / TTS
- [ ] Оставить **один** пайплайн TTS на Google Cloud TTS (`Ru-Ru Neural` + `ru-RU-Wavenet-B`).
- [ ] Удалить дублирующиеся `PostGoogleTts*`, `ИзвлечьMp*`, `Конфиг1М*` — вынести в shared sub-workflow `TTS Generator`.
- [ ] Suno/Lyria — оставить как отдельный tool-call, не смешивать с обычным TTS.

### Этап 4. Исправление поиска
- [ ] Оставить `TavilySearch` как основной.
- [ ] `InternetDeepSearch` — либо явно задепрекейтить, либо дать ему чёткое назначение (например, long-form research без limit).
- [ ] Убрать `Perplexity` из tool-calls, если креды не настроены (сейчас вроде как tool есть, а кредов может не быть).

### Этап 5. Обработка файлов
- [ ] Один универсальный sub-workflow `FileProcessor` для:
  - распознавания типа файла (MIME),
  - выгрузки из Telegram,
  - загрузки в Google Drive с авто-шерингом,
  - возврата ссылки.
- [ ] Из `00` воркфлоу вынести дубли: `GetAFile*`, `Extract*`, `Convert*`, `МассивВТекст*` в один flow.

### Этап 6. Memory и статус
- [ ] Использовать `memoryPostgresChat` с таблицей `Memory_agent_SVOY` как основную.
- [ ] Для краткосрочной памяти — `memoryBufferWindow` с window=20 (сейчас 50 — слишком много для контекста).
- [ ] Добавить sticky note на каждую tool/agent-зону с описанием: что принимает, что возвращает, когда вызывается.

### Этап 7. Vibe и конвенции
- [ ] Все имена нод — на **русском**, но без пробелов/спецсимволов (PascalCase).
- [ ] Sticky Notes обязательны:
  - зелёный = stable / работает
  - жёлтый = deprecated / заменить
  - красный = critical / падает
- [ ] Каждый workflow начинается с sticky-блока:
  - Назначение
  - Вход
  - Выход
  - Ограничения

## 5. Критерии приёмки

- [ ] Главный воркфлоу ≤ 70 нод.
- [ ] ≤ 3 LLM-узла на воркфлоу.
- [ ] Каждый tool-call имеет sticky note с примером входа.
- [ ] Нет дублирующейся логики TTS, File Processing, Image Generation.
- [ ] Unified Assistant Agent включён (`active: true`) и имеет working Memory + fallback LLM.
- [ ] Если агент не может ответить — пользователь получает явное сообщение, а не тишину.

## 6. Что реализуем сначала (следующий slice)

1. Аудит Duff-нод в `00` — отметить для деletes.
2. Создать `docs/N8N_NODES_INVENTORY.md` — маппинг: что есть, что дубль, что нужно оставить.
3. Подготовить `N8N_AGENTS_TZ.md` (этот файл) на ревью.
4. После approve: начать с Этапа 1 (консолидация моделей).

---

## 7. Инцидент: 404 на n8n.aiconicvibe.store (2026-06-26)

### Симптом
`https://n8n.aiconicvibe.store/` отдавал HTTP 404 (text/plain). n8n был недоступен.
Другие домены (evolutionapi, crmamoexuz, crmamoexdubai) тоже не работали.

### Как выявил
1. `curl -sI https://n8n.aiconicvibe.store/` → HTTP 404
2. Зашёл на VPS (`151.241.100.226`):
   - `docker ps` → все контейнеры **Up**, включая n8n-n8n-1 и n8n-traefik-1
   - `docker inspect n8n-n8n-1` → Traefik labels правильные: `Host(n8n.aiconicvibe.store)`, порт 5678
   - `docker logs n8n-traefik-1` → ошибка: `client version 1.24 is too old. Minimum supported API version is 1.44`
   - `docker version` → Docker 29.1.3, Server API version 1.52

### Причина
Docker обновился до версии 29.1.3, которая **отключила поддержку старых API-версий**. Traefik v2.10 (собран с Go Docker SDK, который использует API 1.24) больше не мог общаться с Docker daemon. Traefik не видел лейблы контейнеров → не находил router для n8n → 404.

Traefik v3.3 тоже не помог — его Go-зависимости ещё старые. `traefik:latest` (собран после февраля 2026) не решил проблему полностью, потому что встроенный Go Docker SDK всё равно не читает `DOCKER_API_VERSION`.

### Как решил
1. **Отключил Docker provider** в Traefik (`--providers.docker=false`).
2. **Включил File provider** (`--providers.file.filename=/traefik_dynamic.yml`).
3. **Создал конфиг** `/opt/n8n/traefik_dynamic.yml` с явным описанием:
   - n8n router → `http://127.0.0.1:5678`
   - evolution router → `http://127.0.0.1:8081`
4. Пересоздал контейнер Traefik через `docker compose up -d --force-recreate traefik`.
5. Проверил: `curl -I https://n8n.aiconicvibe.store/` → **HTTP 200**.
6. Проверил `/rest/settings` → n8n API отвечает, UI работает.

### Как предотвратить в будущем
- **При обновлении Docker** до мажорной версии (29 → 30) — сначала проверять совместимость Traefik.
- **Мониторинг**: добавить healthcheck для n8n URL, который дёргает `/rest/settings` раз в минуту и шлёт в Telegram если не 200.
- **Резервный доступ**: через SSH напрямую к n8n (`curl http://127.0.0.1:5678/` с VPS) — чтобы отличать "упал n8n" от "упал reverse proxy".
- **Docker provider vs File provider**: File provider стабильнее — не зависит от Docker API. При переезде на новый хост достаточно скопировать `traefik_dynamic.yml`.
- **watchtower** на VPS (он есть) может автоматически обновлять Traefik — нужно проверить его конфиг, чтобы случайно не воткнул непроверенную версию.
