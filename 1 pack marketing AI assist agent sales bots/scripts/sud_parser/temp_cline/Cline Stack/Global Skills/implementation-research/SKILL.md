---
name: implementation-research
description: Поиск готовых реализаций, production patterns, зрелых repo examples и best practices через локальный код, MCP, Context7, Tavily, Exa и GitHub.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Implementation Research

Этот skill нужен, когда требуется не абстрактный ответ, а сильное техническое решение, основанное на проверяемых источниках и зрелых реализациях.

## Когда использовать
- нужна готовая реализация, а не теория;
- нужен production pattern, mature repo example или canonical implementation;
- нужно интегрировать новый API, SDK, CLI, сервис или фреймворк;
- нужно сравнить несколько подходов и выбрать сильнейший;
- нужно найти не только docs, но и рабочие куски решения.

## Когда НЕ использовать
- задача локальная и ответ уже очевидно есть в кодовой базе;
- нужен точечный edit в известном файле без внешнего исследования;
- вопрос простой, не version-sensitive и не требует готовых примеров;
- достаточно `read_file`, `search_files` или `local-code-search` без внешнего поиска.

## Приоритет источников
1. Локальный код, существующие MCP и доступные внутренние системы.
2. Context7 и официальная документация библиотек/фреймворков.
3. Official guides, official examples и migration/changelog материалы.
4. GitHub MCP для поиска зрелых репозиториев, production patterns и кода.
5. Exa для semantic search, чистых code examples и технических материалов.
6. Tavily для свежих best practices, edge-cases, release context и field reports.
7. Community discussions только как слой workaround’ов и спорных кейсов.

## Routing по типу задачи

### 1. Repo-specific implementation
Если ответ может уже жить в проекте:
- сначала используй `local-code-search`, `search_files`, `read_file` и подходящие MCP;
- только потом иди во внешний поиск.

### 2. Library / SDK / framework usage
Если нужна актуальная реализация на конкретной технологии:
- сначала Context7;
- затем official docs и official examples;
- потом changelog / migration notes;
- только потом community.

### 3. Bug / strange error / edge case
Если задача начинается с ошибки:
- ищи по exact error string, stack trace, коду ответа или симптому;
- проверь official docs, changelog, issues/discussions;
- если официальные источники не дают ответа, подключай Tavily и Exa.

### 4. Production pattern / ready-made implementation
Если нужен зрелый подход:
- используй GitHub MCP, repo search и code search;
- добирай official examples и Exa для чистых материалов;
- выбирай зрелые реализации, а не случайные gist/snippet-примеры.

### 5. Fresh ecosystem knowledge
Если важны свежие изменения API, release notes или текущие best practices:
- используй Tavily и Exa;
- сверяй с official docs, чтобы не принять field report за источник истины.

## Как искать
- Ищи не абстрактную тему, а конкретный сценарий: `retry webhook idempotency`, `oauth callback handler`, `server action form validation`, `billing table filters`, `telegram webhook signature verification`.
- Если нужна реализация, ищи сразу три слоя: official docs, canonical example, mature repo pattern.
- Для GitHub-поиска предпочитай зрелые репозитории с понятным стеком, актуальной структурой и живым кодом.
- Для Exa формулируй запрос как описание идеального решения, а не как набор ключевых слов.
- Для Tavily используй его, когда нужна свежесть, широкий обзор или edge-case контекст.

## Как оценивать качество найденного

### Сильный источник
- официальный;
- зрелый open-source repo;
- production write-up от сильной команды;
- пример совместим с текущим стеком;
- есть контекст, trade-offs и ограничения.

### Слабый источник
- gist или snippet без контекста;
- статья без версии и без кода;
- старый tutorial с устаревшим API;
- случайный пример, который не похож на production;
- решение, требующее лишних зависимостей без явной пользы.

## Как собирать итоговое решение
- Не копируй найденный код вслепую.
- Возьми сильный паттерн и адаптируй его под текущий стек, архитектуру и требования.
- Явно укажи, что взято из official docs, что из repo example, а что является инженерной адаптацией.
- Если источники конфликтуют, зафиксируй это и объясни, почему выбран конкретный вариант.
- Если нет зрелого решения, скажи это прямо и предложи наиболее надёжный паттерн с оговорками.

## Шаблон итогового вывода
- Что искали
- Какие источники использовали
- Какой паттерн выбран
- Почему он лучше альтернатив
- Что нужно адаптировать под текущий стек
- Какие ограничения и риски остались

## Красные флаги
- решение найдено только в одном слабом источнике;
- пример не совпадает по версии API/SDK;
- код красивый, но не покрывает edge-cases;
- найденный паттерн противоречит текущей архитектуре проекта;
- агент начинает сочинять недостающие части вместо честного добора источников.

## Smoke tests

### Smoke test 1 — production pattern
Запрос: `Найди production-grade retry strategy для HTTP-клиента в Python.`

Ожидание:
- official docs + mature repo examples + осмысленный выбор паттерна.

### Smoke test 2 — SDK integration
Запрос: `Покажи рабочий способ авторизации для нового SDK X.`

Ожидание:
- Context7 / official docs first, потом примеры и адаптация под стек.

### Smoke test 3 — mature repo pattern
Запрос: `Найди хороший пример webhook processing с retries и idempotency.`

Ожидание:
- GitHub MCP + official guides + отбор зрелых решений.

### Smoke test 4 — bug + docs + field reports
Запрос: `После обновления пакета ломается auth middleware, найди лучший путь фикса.`

Ожидание:
- exact error / changelog / issues / docs / adaptation.

### Smoke test 5 — transparency
Запрос: `Дай решение и покажи, на чём оно основано.`

Ожидание:
- явное разделение official / repo / community / assumptions.