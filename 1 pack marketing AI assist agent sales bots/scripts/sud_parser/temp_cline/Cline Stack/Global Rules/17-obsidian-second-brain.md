# Obsidian Second Brain / LLM Wiki

## Когда использовать
## Registry note
- Локальный skill `obsidian-second-brain-query` существует на диске, но пока отсутствует в активном system registry.
- Поэтому canonical global routing должен идти через зарегистрированные skills: `obsidian-second-brain`, `obsidian-second-brain-ingest`, `obsidian-second-brain-save`, `obsidian-second-brain-lint`, `obsidian-second-brain-world`.
- Если позже `obsidian-second-brain-query` будет зарегистрирован в system registry, его можно вернуть как отдельную routing-точку.

- Используй skill `obsidian-second-brain`, когда пользователь хочет собрать или обслуживать Obsidian-based второй мозг / LLM wiki.
- Используй `obsidian-second-brain-ingest`, когда в `raw/` появились новые источники и их нужно скомпилировать в wiki.
- Используй `obsidian-second-brain` для query/read workflows по накопленным знаниям vault; при необходимости дополняй `obsidian-second-brain-world` для быстрого восстановления рабочего контекста.
- Используй `obsidian-second-brain-save`, когда нужно сохранить ценный результат сессии обратно в vault.
- Используй `obsidian-second-brain-world`, когда нужно быстро восстановить рабочий контекст из vault.
- Используй `obsidian-second-brain-lint`, когда нужно проверить здоровье vault, broken links, index drift и stale hot cache.

## Каноничный гибридный подход
- `mcp-obsidian` в текущем setup — это read/search слой, а не write API.
- Все записи и обновления в vault должны делаться обычными файловыми инструментами.
- Предпочитай структуру `raw/`, `wiki/`, `output/`.
- Для совместимости с текущим MCP не используй hidden source folders вроде `.raw/`, если хочешь читать их через MCP.

## Каноничные core files
- `wiki/hot.md` — читать первым для восстановления контекста.
- `wiki/index.md` — читать вторым как карту страниц.
- `wiki/overview.md` — high-level карта знаний.
- `wiki/meta/current-focus.md` — текущие приоритеты и активные нити.
- `wiki/log.md` — журнал значимых операций.

## Continuity contract
- `cline_docs/project-state.md` = continuity по текущей задаче.
- `wiki/hot.md` = continuity по knowledge base.
- `wiki/meta/current-focus.md` = operational focus внутри второго мозга.
- Перекладывай результат из task-layer в vault только через осознанный save-back workflow.

## Каноничный порядок чтения
1. `wiki/hot.md`
2. `wiki/index.md`
3. `wiki/overview.md`
4. `wiki/meta/current-focus.md` при релевантности
5. 3–5 конкретных страниц
6. source summaries
7. raw — только как last resort

## Работа с MCP
- Для `read_notes` используй относительные пути (`raw/file.md`, `wiki/index.md`).
- Если vault расположен в symlink path на macOS (например `/tmp`), для MCP-конфига и тестов предпочитай `realpath`.
- Не ожидай от `search_notes` полнотекстового поиска по содержимому — это поиск по именам заметок.
- `search_notes` ищет по имени файла, а не по `title` во frontmatter или body note.
- Для `search_notes` предпочитай короткие частичные запросы (`pricing`, `obsidian`, `inbox`), а не длинные точные фразы из заголовка.
- Если нужен content-level поиск, сначала используй `wiki/index.md` / `wiki/hot.md` / targeted reads или обычный файловый поиск.

## Soft automation policy
- Hooks в second brain workflow должны быть soft reminders, а не auto-write слой.
- После изменений в `wiki/` и `raw/` допустимы мягкие напоминания обновить `wiki/hot.md` и при необходимости `wiki/meta/current-focus.md`.
- Не делай слепую автоматическую синхронизацию между `project-state.md` и vault continuity файлами.

## Inbox / processed policy
- Новые материалы по умолчанию клади в `raw/inbox/`.
- После ingest переводи их в `raw/processed/` или явно фиксируй, что source уже обработан.
- Legacy файлы в корне `raw/` допустимы, но не превращай корень `raw/` в постоянную свалку.

## Review / approve policy
- Для крупных save-back или ingest-изменений используй промежуточный слой `output/review/`.
- Маленькие и безопасные правки можно вносить прямо в live wiki.
- Если структура спорная, сначала review, потом перенос в `wiki/`.

## Live save-back policy
- После **реальной аналитической сессии** сначала сохраняй decision-ready knowledge artifacts, а не сырой transcript.
- Нормальный save-back по живому кейсу обычно включает: 1 главный артефакт (`question` или `comparison`), 1–2 supporting updates и обновление continuity-файлов.
- Если по итогам живой сессии обнаружились устаревшие или вымышленные ссылки, сначала приведи live knowledge layer в честное состояние, а потом обновляй `hot.md` и `current-focus.md`.
- Не создавай новый source summary только потому, что хочется «полноты»; новый внешний source нужен под реальный operational gap.

## Lint scope policy
- При lint различай **live knowledge layer** и template layer.
- Placeholder-ссылки в `CLAUDE.md` и `*_template.md` не считай broken links live-слоя, если это явно шаблонные маркеры.
- Broken links в knowledge pages, index drift и stale continuity — это реальные дефекты и высокий приоритет.
- После framework-level save-back или серии значимых knowledge updates делай lint-pass и фиксируй, что было auto-fixed, а что остаётся manual.

## Entity / graph policy
- Для полезного graph view сначала усиливай `wiki/entities/`, `wiki/concepts/`, synthesis pages и `[[wikilinks]]`.
- Graph View в Obsidian — это следствие хорошей структуры, а не причина её делать.
- Не тащи graph DB, ontology-first architecture или тяжёлый RAG, пока entity layer ещё слабый.
- Если хочется «графы потом», сначала делай connected entities, connected concepts и hub pages.

## Operational cadence
- После каждой реальной аналитической сессии делай save-back в тот же рабочий цикл.
- После серии значимых обновлений или новой framework-level страницы прогоняй lint.
- `wiki/hot.md` обновляй при смене реального operational focus, а не после каждой мелкой правки.
- `wiki/meta/current-focus.md` держи коротким и action-oriented: приоритеты, open threads, next useful reads.

## Когда НЕ переусложнять
- Не добавляй autoresearch, scheduled agents, canvas и фоновую автоматизацию до тех пор, пока не заработал core-loop: scaffold → ingest → query → save → world → lint.
- Не читай весь vault подряд без narrowing через `hot.md` и `index.md`.
- Не дублируй страницы, если можно обновить существующие.

## SessionStart restore
- Если текущий workspace сам является second brain vault, SessionStart может подтягивать `wiki/hot.md` и `wiki/meta/current-focus.md` как lightweight continuity.
- Не загружай весь vault автоматически на старте; хватит hot/focus слоя.

## Compaction hygiene
- PreCompact / SessionStart restore для второго мозга должны быть workspace-aware: marker после compaction нельзя применять к другому workspace.
- Если marker принадлежит другому workspace, SessionStart должен его игнорировать, а не потреблять.
