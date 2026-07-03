# Obsidian Second Brain — Hybrid Architecture

Этот гибрид берёт **core-слой** из `AgriciDaniel/claude-obsidian`, но упрощает его под Cline и установленный `mcp-obsidian`.

## Что берём из AgriciDaniel
- `wiki/index.md` как master catalog;
- `wiki/log.md` как краткий журнал операций;
- `wiki/hot.md` как дешёвый recent-context cache;
- `wiki/overview.md` как high-level карту хранилища;
- `wiki/meta/current-focus.md` как lightweight current-work pointer;
- разделение на операции scaffold / ingest / query / lint / world / save;
- принцип «wiki — это продукт, чат — это интерфейс».

## Что упрощаем
- без canvas-слоя;
- без autoresearch-loop по умолчанию;
- без сложной Obsidian REST API-интеграции;
- без обязательных hooks/cron как части first step;
- без жёсткой привязки к Claude plugin ecosystem.

## Как распределяются обязанности
- `mcp-obsidian` → быстрый поиск и чтение заметок;
- файловые инструменты → создание и обновление markdown-файлов;
- `CLAUDE.md` в корне vault → правила поведения агента;
- `hot.md` → дешёвое восстановление активного контекста;
- `index.md` → карта страниц;
- `overview.md` → high-level карта;
- `current-focus.md` → текущие приоритеты и активные потоки;
- `log.md` → история важных операций.

## Soft automation policy
- Hooks в этом подходе должны **напоминать**, а не молча переписывать vault.
- После изменений в `wiki/` и `raw/` допустимы только soft reminders на refresh `wiki/hot.md` и `wiki/meta/current-focus.md`.
- Auto-write hook без явного согласованного workflow здесь считается оверинжинирингом.

## Минимальный operational loop
1. Положить новый источник в `raw/`.
2. Прогнать ingest.
3. Обновить source summary, entity/concept pages, index, log, hot.
4. Если меняется рабочий приоритет — обновить `current-focus.md`.
5. На queries сначала читать `hot.md`, потом `index.md`, потом 3–5 релевантных страниц.
6. Для быстрого возврата в контекст использовать world-loader.
7. Периодически запускать lint.
8. Для ценных результатов сессии использовать save-back workflow.

## Когда расширять систему
Расширяй её только после того, как заработал core-loop:
- ingest;
- query;
- save;
- lint;
- world-load;
- hot cache;
- понятная структура страниц.

Лишь после этого имеет смысл добавлять research automation, scheduled maintenance, background agents и richer Obsidian integrations.

## SessionStart restore
- Если текущий workspace сам является vault и в нём есть `wiki/hot.md`, SessionStart может подтягивать `wiki/hot.md` и `wiki/meta/current-focus.md` как lightweight continuity.
- Такой restore не должен читать весь vault и не должен заменять `project-state.md`; это отдельный слой knowledge continuity.

## Compaction hygiene
- Recovery marker после compaction должен быть привязан к workspace realpath.
- SessionStart должен применять restore только если marker относится к тому же workspace.
- Marker из другого workspace нельзя потреблять на старте текущего vault/session.
