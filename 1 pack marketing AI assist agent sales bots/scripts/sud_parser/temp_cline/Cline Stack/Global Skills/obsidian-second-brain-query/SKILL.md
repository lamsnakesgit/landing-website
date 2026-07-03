---
name: obsidian-second-brain-query
description: Use when answering questions from an Obsidian second brain vault: search notes, read relevant pages, synthesize an answer, and optionally save valuable results back into the wiki.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Obsidian Second Brain Query

Отвечай на вопросы по vault, не читая весь архив подряд.

## Когда использовать
- «что я знаю про X?»;
- «найди всё по теме Y»;
- «собери сравнение/резюме на основе заметок»;
- нужно извлечь ответ из уже накопленного wiki.

## Когда НЕ использовать
- сначала надо ingest-нуть новый источник;
- нужен health check структуры vault, а не ответ по знаниям.

## Workflow
1. Сначала прочитай `wiki/hot.md`.
2. Затем прочитай `wiki/index.md`.
3. Если вопрос про текущую работу/приоритеты — также прочитай `wiki/meta/current-focus.md`.
4. Используй `mcp-obsidian` (`search_notes`) для поиска кандидатов **по имени файла/заметки**, а не по содержимому.
5. Ищи короткими и частичными запросами (`pricing`, `obsidian`, `inbox`), а не длинной точной фразой из заголовка.
6. Если нужен content-level поиск, не полагайся на `search_notes`: используй `hot.md`, `index.md`, targeted reads и обычный файловый поиск.
7. Используй `read_notes` для чтения 3–5 самых релевантных страниц.
8. Если ответа не хватает — дочитай source summaries, а raw используй как last resort.
9. Ответ давай с ссылками вида `[[Page Name]]`.
10. Если ответ ценный и переиспользуемый — предложи сохранить его в `wiki/questions/` или `wiki/comparisons/`.

## Практические правила
- паттерн чтения: `hot -> index -> current-focus (when relevant) -> targeted pages`;
- не сканируй весь vault без причины;
- сначала доверяй wiki-страницам, потом source summaries, и только потом raw;
- полезные synthesis-ответы должны компаундиться обратно в vault;
- `search_notes` хорош для discovery по имени файла, но не заменяет полнотекстовый поиск.

## Smoke tests
- «Что у меня накоплено по теме pricing?» → skill читает hot/index, ищет релевантные страницы, собирает ответ с wikilinks.
- «Сравни два подхода на базе моих заметок» → skill создаёт structured comparison и предлагает сохранить.
- `search_notes("Inbox Protocol")` не находит `inbox-protocol.md`, а `search_notes("inbox")` находит — skill должен учитывать этот паттерн и не принимать его за сбой содержимого.

## Red flags
- читать десятки файлов без narrowing через hot/index/search;
- отвечать без ссылок на страницы;
- не предлагать сохранить реально полезную synthesis-страницу;
- ожидать, что `search_notes` ищет по frontmatter title или body note.
