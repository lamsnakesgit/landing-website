---
name: obsidian-second-brain-lint
description: Use when auditing an Obsidian second brain vault for broken links, orphan pages, stale claims, missing index entries, weak cross-references, and hot-cache drift.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Obsidian Second Brain Lint

Проверяй здоровье vault и находи structural drift до того, как wiki превратится в мусорку.

## Когда использовать
- пользователь просит audit / lint / health check;
- после серии ingest-ов;
- после framework-level save-back или живой аналитической сессии;
- перед важной query или synthesis-работой.

## Когда НЕ использовать
- нужен import нового источника;
- нужен ответ по уже существующему знанию.

## Что проверять
1. Broken wikilinks в **live knowledge pages**
2. Orphan pages без inbound links
3. Consistency `wiki/index.md`
4. Stale claims и страницы, давно не обновлявшиеся при наличии новых source pages
5. Missing pages и missing cross-references
6. Freshness `wiki/hot.md` относительно последних записей в `wiki/log.md`
7. Freshness `wiki/meta/current-focus.md` относительно hot/log
8. Template drift — страницы, которые слишком далеко ушли от agreed structure
9. Distinction between live layer and template placeholders

## Workflow
1. Собери findings по всем категориям.
2. Сначала отдели **live knowledge findings** от template-only noise.
3. Сгруппируй findings по severity: errors / warnings / info.
4. Сформируй markdown-отчёт по шаблону `wiki/meta/lint-report-template.md`.
5. Отдельно выдели, что можно auto-fix, а что требует подтверждения пользователя.
6. Не чини ничего рискованного без явного согласования.
7. После фиксов обнови `wiki/log.md`.
8. Если lint меняет структуру понимания текущих priorities — обнови `wiki/hot.md` и при необходимости `current-focus.md`.

## Live layer policy
- Placeholder-ссылки в `CLAUDE.md` и `*_template.md` не считай broken links knowledge-слоя, если это явно шаблонные маркеры вроде `[[Page Name]]`.
- Broken links в `wiki/questions/`, `wiki/concepts/`, `wiki/comparisons/`, `wiki/sources/`, `wiki/index.md`, `wiki/hot.md` и `wiki/meta/current-focus.md` — это реальные operational defects.
- Если живая сессия вскрыла вымышленные или отсутствующие страницы, это не cosmetic issue: нужно либо создать реальный artifact, либо убрать stale reference.

## Safe-fix policy
### Разрешено auto-fix без высокого риска
- добавить отсутствующую index entry, если page явно существует и категория однозначна;
- исправить очевидный broken wikilink, если target однозначен;
- создать report file в `wiki/meta/`;
- дописать missing frontmatter fields по agreed minimal schema, если значения можно вывести детерминированно;
- исключить template placeholder noise из lint-отчёта.

### Только после подтверждения пользователя
- удаление/слияние страниц;
- массовый rewrite cross-links;
- правка спорных stale claims;
- любые изменения, где есть несколько правдоподобных target pages;
- изменение `current-focus.md`, если это уже интерпретация, а не явный drift.

## Формат lint-отчёта
Используй один markdown-отчёт, где есть:
- Summary
- Errors
- Warnings
- Info
- Safe fixes applied
- Suggested manual fixes

## Практические правила
- lint должен сначала диагностировать, потом уже чинить;
- broken links и index drift — highest priority;
- stale `hot.md` и `current-focus.md` — operational defects, а не косметика;
- не auto-fix ambiguous knowledge changes;
- после живой сессии лучше короткий честный lint, чем длинный шумный отчёт с template noise.

## Smoke tests
- «Проверь мой vault на structural problems» → skill даёт отчёт с severity и файлами.
- «Найди, где index разошёлся с реальными страницами» → skill сверяет каталог и файлы.
- «Исправь только безопасные проблемы» → skill чинит low-risk drift и отдельно перечисляет, что не тронул.
- «Прогони lint после живой pricing-сессии» → skill отличает реальные broken links от placeholder-шумов шаблонов.

## Red flags
- автофиксить всё без отчёта и согласования;
- игнорировать hot cache freshness;
- считать orphan pages всегда ошибкой без анализа, intentional ли это singleton page;
- переписывать знания ради красоты структуры;
- смешивать template placeholders и live defects в один severity bucket.
