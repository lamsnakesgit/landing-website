# {{VAULT_NAME}} — Obsidian Second Brain

Purpose: {{PURPOSE}}
Updated: {{DATE}}

## Architecture

- `raw/` — входящие и уже обработанные источники. Не переписывать исходники без явной причины.
- `raw/inbox/` — место для новых источников, которые ещё не прошли ingest.
- `raw/processed/` — место для источников, которые уже были обработаны или переобработаны.
- `wiki/` — рабочая knowledge base, которую ведёт агент.
- `output/` — экспорт, review-артефакты и производные файлы.
- `output/review/` — промежуточные материалы для approve/review перед крупным save-back.

## Core files

- `wiki/hot.md` — краткий recent context cache. Читать первым.
- `wiki/index.md` — каталог страниц. Читать вторым.
- `wiki/overview.md` — high-level карта базы знаний.
- `wiki/meta/current-focus.md` — текущие приоритеты и активные нити работы.
- `wiki/log.md` — журнал важных операций.

## Wiki directories

- `wiki/sources/` — summary pages по источникам.
- `wiki/entities/` — люди, компании, продукты, репозитории, инструменты.
- `wiki/concepts/` — идеи, паттерны, методы, темы.
- `wiki/comparisons/` — сравнения и synthesis pages.
- `wiki/questions/` — сохранённые ответы на полезные вопросы.
- `wiki/meta/` — отчёты, conventions, focus и audit files.

## Operating rules

1. Сначала ищи существующие страницы, потом создавай новые.
2. На запросах сначала читай `wiki/hot.md`, потом `wiki/index.md`, потом `wiki/overview.md`, потом конкретные страницы.
3. Новые входящие материалы сначала складывай в `raw/inbox/`. После ingest перемещай их в `raw/processed/` или явно фиксируй, что это legacy source в корне `raw/`.
4. После ingest или значимой query/update обязательно обновляй `wiki/log.md` и `wiki/hot.md`.
5. Если изменился текущий приоритет или активный поток работы — обновляй `wiki/meta/current-focus.md`.
6. Все внутренние ссылки оформляй как `[[Page Name]]`.
7. Предпочитай обновление существующей страницы дублированию.
8. Для поиска и чтения заметок можно использовать `mcp-obsidian`, но запись делай обычными файловыми инструментами.
9. Для крупных save-back или ingest-операций сначала можно собрать candidate-артефакт в `output/review/`, потом переносить в live wiki.
10. Если живая сессия выявила stale refs или вымышленные страницы, сначала cleanup live layer, потом refresh continuity.

## Graph-friendly policy

- Не строй graph database на старте; сначала делай качественные `entities`, `concepts`, `comparisons`, `questions`.
- Graph View в Obsidian должен быть следствием хороших `[[wikilinks]]`, а не самоцелью.
- Для entity pages явно поддерживай связи: connected entities, connected concepts, source references.
- Для graph-friendly обзора предпочитай hub/synthesis pages вместо хаотичного множества слабых заметок.

## Minimal frontmatter

```yaml
---
type: source|entity|concept|comparison|question|meta
title: "Human readable title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
related: []
sources: []
---
```

## Optional frontmatter for richer graph pages

```yaml
aliases: []
entity_type: person|company|tool|product|repo|topic
confidence: low|medium|high
```
