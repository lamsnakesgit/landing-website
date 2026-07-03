---
name: obsidian-second-brain-world
description: Use when you need to quickly restore working context from an Obsidian second brain vault via hot cache, index, overview, current focus, and a few targeted pages.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Obsidian Second Brain World

Быстро восстанавливай рабочий контекст без чтения всего vault.

## Когда использовать
- в начале новой сессии;
- когда нужно быстро понять, чем пользователь занят сейчас;
- перед длинной задачей, если vault уже ведётся;
- после compaction или handoff.

## Когда НЕ использовать
- нужен глубокий ingest нового источника;
- пользователь задал узкий фактологический вопрос и достаточно query workflow.

## Workflow
1. Прочитай `wiki/hot.md`.
2. Прочитай `wiki/index.md`.
3. Прочитай `wiki/overview.md`.
4. Если существует, прочитай `wiki/meta/current-focus.md`.
5. При необходимости дочитай 1–3 targeted pages по текущему фокусу.
6. Верни краткий boot-up summary: текущие приоритеты, активные темы, открытые вопросы, что нужно дочитать дальше.

## Практические правила
- это boot sequence, а не deep research;
- не читай весь vault для world-load;
- если `current-focus.md` устарел, скажи об этом и предложи обновить позже через обычный workflow.

## Smoke tests
- «Подними мне контекст по vault перед началом работы» → skill читает hot/index/overview/current-focus и возвращает краткую сводку.
- «Что у меня сейчас в фокусе по второму мозгу?» → skill отвечает на базе current-focus + hot.

## Red flags
- превращать world-loader в ingest/query/lint сразу;
- читать десятки страниц без причины;
- смешивать boot summary с длинным анализом.
