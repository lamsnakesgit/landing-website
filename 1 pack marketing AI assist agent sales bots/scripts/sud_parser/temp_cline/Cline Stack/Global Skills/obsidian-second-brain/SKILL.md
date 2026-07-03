---
name: obsidian-second-brain
description: Use when building or operating an Obsidian-based second brain / LLM wiki with Cline and mcp-obsidian. Good for vault scaffold, hot cache, index/log structure, persistent context, and routing ingest/query/save/lint/world workflows.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Obsidian Second Brain

Гибридный skill по мотивам Karpathy LLM Wiki и `AgriciDaniel/claude-obsidian`, упрощённый под Cline + локальный `mcp-obsidian`.

## Когда использовать
- пользователь хочет собрать второй мозг в Obsidian;
- нужно scaffold-нуть vault под LLM Wiki;
- нужен persistent context через `wiki/hot.md`, `wiki/index.md`, `wiki/log.md`;
- нужно договориться о структуре vault и правилах обновления знаний;
- нужно понять, как использовать `mcp-obsidian` вместе с обычными файловыми инструментами.

## Когда НЕ использовать
- нужен только разовый поиск по markdown без полноценного vault workflow;
- нужен rich REST API к Obsidian plugin вместо filesystem/MCP hybrid;
- задача не про knowledge base, а просто про заметки или docs.

## Ключевые решения этого гибрида
- `mcp-obsidian` в текущей установке используется как **read/search слой**, а не как write API.
- Все записи и правки делаются обычными файловыми инструментами (`Read/Write/Edit/Bash`).
- Для совместимости с установленным `mcp-obsidian` предпочитай `raw/`, а не `.raw/`, потому что hidden directories этим сервером не читаются.
- Держи core-артефакты маленькими и поддерживаемыми: `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, `wiki/meta/current-focus.md`.
- Сначала читай `hot.md`, потом `index.md`, потом `overview.md`, и только потом конкретные страницы.
- Различай **live knowledge pages** и template layer: placeholder в шаблоне — не то же самое, что broken link в рабочей knowledge page.

## Continuity contract
- `cline_docs/project-state.md` = continuity по текущей задаче/рабочему циклу.
- `wiki/hot.md` = continuity по знаниям vault.
- `wiki/meta/current-focus.md` = текущие приоритеты и активные потоки внутри второго мозга.
- Не пытайся синхронизировать эти слои вслепую; связывай их только через осознанные save/update workflows.

## Workflow
1. Определи vault path и назначение хранилища.
2. Если vault ещё не подготовлен — используй `scripts/scaffold_vault.sh` или шаблоны из `templates/vault/`.
3. Создай или обнови корневой `CLAUDE.md`, чтобы у агента были правила структуры и обновления знаний.
4. Проверь, что `mcp-obsidian` смотрит в правильный каталог vault.
5. Для новых источников используй skill `obsidian-second-brain-ingest`.
6. Для ответов по накопленным знаниям используй skill `obsidian-second-brain-query`.
7. Для сохранения ценных результатов сессии используй skill `obsidian-second-brain-save`.
8. Для восстановления рабочего контекста используй skill `obsidian-second-brain-world`.
9. Для health-check и cleanup используй skill `obsidian-second-brain-lint`.
10. После значимых изменений обновляй `wiki/hot.md`, `wiki/log.md` и при необходимости `wiki/meta/current-focus.md`.

## Live operating loop
Используй как каноничный цикл:
1. `world/query` — быстро восстановить контекст и ответить на задачу.
2. `save` — сохранить только decision-ready knowledge artifacts.
3. `clean` — убрать stale references или drift, если живая сессия выявила рассинхрон.
4. `lint` — прогнать health-check после framework-level save-back или серии значимых изменений.

## Operational upgrades to prefer
- Новые источники лучше класть в `raw/inbox/`, а после ingest переводить в `raw/processed/`.
- Для крупных обновлений используй `output/review/` как approve-слой перед переносом в live wiki.
- Усиливай `wiki/entities/` как базу для будущего graph view вместо раннего перехода к graph DB.
- Строй graph-friendly navigation через хорошие entity pages, synthesis pages и `[[wikilinks]]`, а не через тяжёлую инфраструктуру.

## Базовая структура vault
```
<vault>/
├── raw/
│   ├── inbox/
│   ├── processed/
│   └── assets/
├── wiki/
│   ├── index.md
│   ├── log.md
│   ├── hot.md
│   ├── overview.md
│   ├── sources/
│   ├── entities/
│   ├── concepts/
│   ├── comparisons/
│   ├── questions/
│   └── meta/
│       ├── current-focus.md
│       ├── lint-report-template.md
│       ├── ingest-report-template.md
│       └── save-report-template.md
├── output/
│   └── review/
└── CLAUDE.md
```

## Что читать в комплекте
- `docs/hybrid-architecture.md` — карта архитектуры и ограничений гибрида.
- `docs/mcp-obsidian-notes.md` — что умеет и чего не умеет текущий MCP.
- `docs/continuity-contract.md` — как разводить task continuity и vault continuity.
- `templates/vault/` — стартовые шаблоны файлов vault и страниц.
- `scripts/scaffold_vault.sh` — быстрый scaffolding пустого vault.

## Smoke tests
- «Собери мне Obsidian second brain под Cline и mcp-obsidian» → skill создаёт структуру, core-файлы и правила.
- «Как нам организовать hot cache и index для vault?» → skill предлагает `hot.md`, `index.md`, `log.md`, `overview.md`, `current-focus.md`.
- «У меня уже есть vault, как адаптировать его под LLM Wiki?» → skill делает gap analysis и предлагает минимальную миграцию.
- «Проведи живую аналитическую сессию и сохрани результат во второй мозг» → skill маршрутизирует через query/save/lint и требует сохранить knowledge artifact, а не transcript.
- «Хочу красивее и полезнее graph view» → skill сначала усиливает entities / links / synthesis layer, а не тащит graph database.

## Red flags
- складывать всё в один giant markdown файл без `index.md` и `hot.md`;
- писать только через MCP и забывать, что текущий `mcp-obsidian` не является полноценным write API;
- делать hidden source folders, если хочешь читать их через этот MCP;
- читать весь vault подряд вместо схемы `hot -> index -> targeted pages`;
- путать placeholder links в шаблонах с дефектами live knowledge layer;
- рано тащить graph DB, если entity layer и links ещё слабые.
