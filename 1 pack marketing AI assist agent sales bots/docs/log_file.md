# LOG FILE — AI Agents & Sales Bots

## 2026-05-21 — Design: Генерация медиа-ассетов (карусели/Reels) и деплой на Vercel

### ✅ Что сделано (Wins / Победы):
1. **Экспорт ассетов**: Успешно сгенерированы 5 картинок-слайдов PNG (1080x1350px) и Reels-видео MP4 с анимацией переходов (1080x1920px, длительность ~34 сек) с помощью Playwright Chromium и FFmpeg.
2. Картинки запакованы в ZIP-архив `face_to_face_carousel.zip`.
3. Добавлен блок скачивания с кнопками для видео (MP4) и картинок (ZIP) на последний слайд презентации.
4. Скрыты все управляющие элементы интерфейса (кнопки, точки, прогресс-бар) в режиме экспорта `.export-mode`.
5. Водяной знак `@buycryptocash1` бережно сохранен на всех скриншотах и в видео.
6. Выполнен успешный деплой на Vercel: https://f2fcompany.vercel.app.

### 🔴 Проблемы / Issues:
- Playwright TimeoutError: При кликах по `.dot` возникала ошибка из-за их скрытия в `.export-mode`. Исправлено переходом на ArrowDown.
- Ошибка ENOSPC (нехватка места на диске): Установка Chromium упала, но была решена очисткой кэша NPM (`npm cache clean --force`), освободившей 2.9 ГБ.

### 📋 Следующие шаги:
1. Показать пользователю результаты и получить обратную связь по готовому сайту и ассетам.

---

## 2026-05-17 — Правило по `.env` и секретам усилено

### ✅ Что сделано:
1. В project rules добавлено явное правило для `.env`, `.env.*`, секретов и API ключей.
2. Зафиксировано, что без прямого разрешения пользователя агент может только добавлять новые переменные.
3. Удаление, переименование, перезапись и замена существующих env-значений запрещены без явного подтверждения.

### 🎯 Причина:
- Избежать потери существующих env-настроек и секретов при быстрых правках.
- Снизить риск повторного инцидента с нежелательным изменением `.env`.

---

## 2026-04-15 — Стратегическая сессия: Outreach Pipeline + Рабочий процесс

### ✅ Что сделано (Wins / Победы):
1. Проведён полный аудит текущей инфраструктуры и документации
2. Создан стратегический план: AI-агенты + WhatsApp Outreach + B2B лидген
3. Определена архитектура гибридного подхода (n8n + код)
4. Спроектирована схема БД для лидов, сообщений и кампаний
5. Исследованы API 2ГИС, HH.ru, Evolution API — текущие ограничения
6. Определён мобильный workflow: SSH → VPS → tmux → Cline CLI

### 🔴 Проблемы / Issues:
- n8n инстанс не отвечает (404 при запросе списка workflows) — нужна проверка VPS
- Парсинг 2ГИС — юридические риски, нужно решить: API vs покупка данных
- WhatsApp через Evolution API — высокие риски бана при холодной рассылке
- HH.ru ужесточил доступ к API (декабрь 2025) — ограничения для парсеров

### 📋 Следующие шаги:
1. Получить ответы на Open Questions (город, номера, бюджет)
2. Настроить мобильный доступ (SSH + tmux на VPS)
3. Создать Supabase таблицы
4. Начать с парсера (2ГИС или HH.ru — по приоритету)

---

## 2026-04-15 — Стратегическая сессия: Outreach Pipeline + Рабочий процесс (РУССКИЙ)

### ✅ Победы:
1. Провели полный аудит инфраструктуры и документации
2. Создали стратегический план: AI-агенты + WhatsApp Аутрич + B2B лидген
3. Определили гибридный подход (n8n для интеграций, код для парсинга и UI)
4. Спроектировали схему БД Supabase для лидов, сообщений, кампаний
5. Исследовали текущие API ограничения: 2ГИС, HH.ru, Evolution API

### 🔴 Проблемы:
- n8n инстанс не отвечает (ошибка 404) — надо проверить VPS
- 2ГИС парсинг — юридические риски, нужно легальное решение
- WhatsApp — высокий риск бана при холодном аутриче
- HH.ru — ужесточённый доступ к API с конца 2025

### 📋 Дальнейшие шаги:
1. Ответить на открытые вопросы из плана
2. Настроить мобильный доступ к VPS
3. Создать таблицы в Supabase
4. Начать парсер для первой ниши

---

## Предыдущие записи

## 2026-05-16 — Hermes Assistant: базовая архитектура личного и бизнес-ассистента

### ✅ Что сделано (Wins / Победы):
1. Проведён быстрый аудит текущего репозитория на предмет готовых артефактов для Telegram assistant, Fathom/Zoom, памяти, summary и мультимодальности.
2. Подтверждено, что в проекте уже есть сильная основа для MVP: Telegram intake, Whisper/STT, summary pipeline, Fathom post-meeting spec.
3. Зафиксировано архитектурное решение: **Hermes как front-assistant в Telegram**, **n8n как orchestration/integration engine**, **Supabase как persistent memory + RAG + storage**.
4. Отдельно выделен контур встреч: Fathom/Zoom → webhook/poller → summary + timecodes + action items + follow-up → Telegram / Notion / Asana.
5. Сформулировано решение по chat monitoring: для групп и массовых каналов лучше делать отдельный агент/контур, а не смешивать всё в одном персональном боте.

### 🔴 Проблемы / Issues:
- Hermes как конкретный продукт/рантайм пока не зафиксирован на уровне live deployment: на этом шаге утверждена архитектура, но не выполнена установка/подключение runtime.
- Нет ещё финальной матрицы по моделям для image/video/voice generation и по SLA между «быстрым личным ответом» и тяжёлыми фоновыми задачами.
- Не определён финальный policy по правам доступа: что бот может делать сам, а что только после подтверждения.

### 📋 Следующие шаги:
1. Собрать master-spec `Hermes Assistant` с capability map: tasks, memory, RAG, media, meeting intelligence, integrations.
2. Определить MVP-v1: Telegram text/voice/audio/files + web search + task capture + memory + Notion/Asana + Fathom summaries.
3. Выбрать runtime-контур: Hermes/OpenClaw/гибрид, и отдельно решить где живёт planner, где tool execution, где long-term memory.
4. После этого перейти к сборке n8n workflows и backend storage под выбранную схему.

## 2026-05-16 — Hermes vs OpenClaw: установка, runtime и учёт расходов

### ✅ Что подтверждено по источникам:
1. По официальному GitHub и docs Hermes позиционируется как self-improving persistent agent с Telegram gateway, cron, MCP, memory и skills.
2. Official docs Hermes прямо покрывают сценарии: Telegram assistant, team bot, memory, cron scheduling, voice mode, MCP servers, multiple terminal backends.
3. Community-гайды и обзоры сходятся в том, что Hermes особенно хорош, когда нужен **долгоживущий personal assistant на VPS**, а не просто dev-tool.
4. По community/open guides OpenClaw силён в multi-agent, dashboards, plugin ecosystem и control surfaces, но по security-практике требует заметно более осторожного hardening.
5. Для твоего кейса — личный + бизнес ассистент, Fathom, Notion/Asana, медиа, память, проекты — Hermes выглядит как более прямой fit, а n8n остаётся сильным orchestration-слоем.

### 🔴 Практические выводы:
- **Ставить Hermes первым** имеет смысл, если нужен агент «как человек в чате», который ведёт память, проекты, recurring задачи и живёт в Telegram.
- **n8n не заменять**, а использовать под интеграции, webhook flows, Fathom/Zoom ingest, Notion/Asana sync, отчётность и фоновые пайплайны.
- **OpenClaw не выбрасывать**, но держать как отдельную future-ветку под swarm, chat-monitoring, dashboards или multi-agent routing, если Hermes Core станет узким местом.

### 💸 Что важно по cost tracking:
- Реальная стоимость чаще упирается не в VPS, а в **LLM API usage**.
- Нужен явный routing по типу задач:
  - дешёвые модели → triage, summaries, search condensation;
  - средние → рабочие бизнес-задачи и project management;
  - дорогие → стратегия, сложный reasoning, важные решения, premium writing.
- Учёт расходов лучше вести через отдельные таблицы `model_usage`, `task_runs`, `provider_costs`, `monthly_budgets` в Supabase/Postgres.
- Для image/video generation тоже нужен отдельный журнал провайдера, модели, job type, duration/asset count, status и estimated cost.

### 📋 Следующие шаги:
1. Сделать спецификацию установки Hermes именно под твой стек: Telegram + n8n + Supabase + Fathom + Notion/Asana.

## 2026-05-16 — Инициация развёртывания Hermes (Personal + Outreach)

**Задачи:**
1. Подготовка плана развёртывания (Personal Assistant + Outreach Sub-agent).
2. Выбор Hermes Agent в качестве основного ядра.
3. Определение n8n как слоя для бизнес-логики аутрича.

**Результаты:**
- Создан [implementation_plan.md](file:///Users/higherpower/.gemini/antigravity/brain/c7e0e523-336e-4eb1-976a-bdaf06ca0afe/implementation_plan.md).
- Сформулированы вопросы по VPS и площадкам для поиска клиентов.

**Проблемы:**
- Требуется IP адрес VPS для начала удаленной настройки.

2. Спроектировать схему project/memory/cost tables.
3. Определить model routing matrix: какая модель для каких задач.
4. После этого уже идти в live install/runtime setup.

## 2026-05-21 — Config: Восстановление .env и ключи API

### ✅ Что сделано (Wins / Победы):
1. Восстановлены критически важные переменные окружения Evolution API из резервной копии `.env.cline-backup` в файл `.env`.
2. Добавлен `OPENAI_API_KEY` (с предоставленным ключом `sk-8EobYRv...`), необходимый для функционирования ИИ-агентов.
3. Добавлен `GRSAI_API_KEY` (с предоставленным ключом `b57f87b9...`), необходимый для интеграции с моделями GRS AI.
4. Все переменные окружения успешно объединены в файле `.env` с сохранением работоспособности существующих конфигураций.

### 🔴 Проблемы / Issues:
- Пользователь допустил синтаксическую ошибку в терминале при попытке дописать ключ (`cat GRSAI_API_KEY=... >> .env` вместо `echo`), из-за чего `.env` оказался пуст. Проблема решена путем оперативного восстановления из бэкапа и записи корректной конфигурации.

### 📋 Следующие шаги:
1. Проверить интеграцию OpenAI API в сценариях n8n.
2. Проверить работу API-ключей в сопутствующих скриптах.

## 2026-05-15 — Infra: GitHub MCP + Context7 для Cline

### ✅ Что сделано (Wins / Победы):
1. Загружена MCP-документация и повторно прочитан существующий `cline_mcp_settings.json` перед изменениями.
2. По официальным источникам выбраны серверы `github.com/github/github-mcp-server` и `github.com/upstash/context7`.
3. Созданы локальные директории `/Users/higherpower/Documents/Cline/MCP/github.com/github/github-mcp-server` и `/Users/higherpower/Documents/Cline/MCP/github.com/upstash/context7`.
4. В `cline_mcp_settings.json` аккуратно добавлены новые MCP-серверы без перезаписи уже существующих `github.com/VapiAI/mcp-server`, `github.com/exa-labs/exa-mcp-server` и `github.com/tavily-ai/tavily-mcp`.
5. Для GitHub MCP устранено небезопасное хранение секрета: токен убран из JSON и заменён на runtime-чтение через `gh auth token` при запуске Docker-контейнера.
6. Для Context7 настроен локальный запуск через `npx -y @upstash/context7-mcp`.
7. Выполнен smoke test Context7: пакет запускается и отдаёт корректный `--help`.

### 🔴 Проблемы / Issues:
- GitHub MCP не прошёл runtime smoke test не из-за конфига, а из-за состояния локальной среды: Docker daemon недоступен (`Cannot connect to the Docker daemon ...`).
- Context7 установлен без API key, поэтому будет работать с более ограниченными лимитами до последующего добавления ключа.

### 📋 Следующие шаги:
1. Запустить Docker Desktop / Docker daemon на macOS.
2. После запуска Docker перепроверить GitHub MCP фактическим стартом сервера.
3. При необходимости добавить `CONTEXT7_API_KEY` в конфиг для повышения лимитов и стабильности.

## 2026-05-14 — Infra: Exa MCP server для Cline

### ✅ Что сделано (Wins / Победы):
1. Загружена MCP-документация и соблюдён безопасный порядок установки.
2. Прочитан существующий файл `cline_mcp_settings.json` перед изменением, чтобы не перезаписать уже подключённый `github.com/VapiAI/mcp-server`.
3. Создана отдельная локальная директория `/Users/higherpower/Documents/Cline/MCP/github.com/exa-labs/exa-mcp-server` под новый MCP server.
4. Установлен npm-пакет `exa-mcp-server` в локальную директорию.
5. В `cline_mcp_settings.json` добавлен сервер с именем `github.com/exa-labs/exa-mcp-server`, параметрами `disabled: false` и `autoApprove: []`.
6. Проверена работоспособность через тестовый вызов инструмента Exa `web_search_exa`.

### 🔴 Проблемы / Issues:
- `npm install exa-mcp-server` сообщил о 3 уязвимостях зависимостей (`2 moderate`, `1 high`) в установленном пакете/его дереве зависимостей.
- API key временно сохранён в MCP-конфиге в открытом виде, так как именно этот формат нужен для запуска сервера в текущем окружении.

### 📋 Следующие шаги:
1. При необходимости перевыпустить Exa API key и заменить его в `cline_mcp_settings.json`.
2. При следующем проходе по инфраструктуре проверить, можно ли перевести хранение ключа на более безопасную схему.
3. Использовать Exa MCP для web-research задач, где нужен быстрый поиск и извлечение контента.

## 2026-05-14 — Fix: WhatsApp Summary Agent webhook (Evolution API)

### ✅ Что сделано (Wins / Победы):
1. Прочитан `docs/handoff_summary.md` и подтверждено, что проблема находится в связке Evolution API → n8n webhook.
2. Найден релевантный шаблон `n8n_templates/WhatsApp_Summary_Agent_Evolution_API.json`.
3. Выявлена вероятная причина: у ноды `Evolution Webhook` отсутствовал явный параметр `httpMethod: "POST"`.
4. В JSON добавлена явная настройка `POST` для webhook-trigger, чтобы принимать входящие события от Evolution API корректно.
5. Выявлено второе ограничение: workflow пропускал только `audioMessage`, поэтому обычные текстовые сообщения из общей группы не доходили до AI-обработки.
6. Добавлена отдельная ветка `Extract Text Message`, которая достаёт текст из `conversation` / `extendedTextMessage.text` и отправляет его сразу в `Summary AI Agent`.

### 🔴 Проблемы / Issues:
- В handoff упоминаются старые имена файлов (`whatsapp_to_telegram_media_bridge_v2.json`, `whatsapp_to_tg_bridge_fixed.json`), которых сейчас нет по точному имени в дереве проекта.
- Живой runtime n8n и настройки Evolution Manager в этом шаге не проверялись автоматически, поэтому после импорта нужен ручной smoke test.

### 📋 Следующие шаги:
1. Импортировать/обновить `n8n_templates/WhatsApp_Summary_Agent_Evolution_API.json` в n8n.
2. В Evolution Manager проверить webhook URL и убедиться, что включено событие `MESSAGES_UPSERT`.
3. Если планируется голос/медиа — убедиться, что включена передача `Base64`.
4. Отправить тестовое сообщение в WhatsApp и проверить, что execution в n8n стартует сразу на webhook.
5. Отправить в общую группу обычный текст и убедиться, что он проходит по ветке `Extract Text Message`, даже если это не голосовое сообщение.

## 2026-04-15 — Telegram Meeting Assistant MVP

### ✅ Что сделано (Wins / Победы):
1. Собран новый n8n JSON-шаблон `telegram_meeting_assistant_mvp.json`.
2. Добавлен intake для Telegram `text`, `voice`, `audio`, `document audio`.
3. Поддержаны аудио-расширения `.m4a`, `.mp3`, `.wav`, `.aac`, `.ogg` на уровне детекции.
4. Добавлен STT шаг через Whisper HTTP endpoint.
5. Добавлена multi-agent цепочка: summary → sales analysis → content draft.
6. Подготовлен Telegram reply layer с итоговым ответом в один поток.

### 🔴 Проблемы / Issues:
- Текущий шаблон ещё не доведён до production-проверки через импорт в реальный n8n.
- `video` и `video_note` пока не реализованы полноценно, только заложены как следующий этап.
- Нужна ручная подстановка credentials для Telegram и Gemini.

### 📋 Следующие шаги:
1. Импортировать JSON в n8n.
2. Подставить Telegram credentials и Gemini credentials.
3. Протестировать 4 кейса: `text`, `voice`, `audio`, `m4a`.
4. После проверки расширить workflow до `video/video_note`.
5. Затем подключить Fathom webhook в общий processing layer.

## 2026-04-12
- Реструктуризация проекта на 6 доменов
- Создан tg_to_whatsapp.json workflow
- Создан gemini_carousel_generator.json

## 2026-04-08
- Начата разработка AI лидген системы
- Спроектирована CRM архитектура в Supabase
- Определена стратегия rate-limiting для WA
