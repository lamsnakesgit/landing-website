# Правила работы с проектами пользователя

## Технический стек и инфраструктура
> 📁 Подробная информация: **`tech-stack.md`** (в той же папке Rules)
> MUST читать `tech-stack.md` при работе с сервером, деплоем, VPS или инфраструктурой.

**Кратко:** Python/FastAPI, Node.js/TypeScript, N8N, Claude API, Railway, Docker, PostgreSQL, Redis, Supabase, aiogram.

### 🚨 При создании нового сервиса — MUST обновить `tech-stack.md`

## .clineignore

- MUST добавлять `.clineignore` в каждый новый проект.
- Без `.clineignore` Cline загружает слишком много лишнего контекста.
- Используй шаблоны из `~/Documents/Cline/Templates/` по стеку проекта.
- Файлы из `.clineignore` можно явно подтянуть через `@path/to/file`, если они реально нужны в задаче.

## При старте нового проекта
1. MUST проверить, есть ли уже файлы проекта в рабочей директории.
2. MUST изучить README.md и другие `*.md` файлы с описанием.
3. SHOULD уточнить недостающие требования, если без них нельзя безопасно спроектировать решение.
4. MUST определить канонический project label для текущей сессии. Если существует `.clinerules/{project-name}.md`, используй имя этого файла как основной идентификатор проекта в формате `Проект: {project-name}.md`.
5. MUST создать текущий исполнимый чек-лист в `task_progress`.
6. Для длинной / multi-phase задачи MUST создать или обновить канонический global plan в `implementation_plan.md`, `docs/plan.md` или аналогичном plan file.
7. SHOULD предложить создать Memory Bank через `initialize memory bank`.
8. SHOULD создать `cline_docs/project-state.md`, если задача предполагает длительную работу, handoff или несколько этапов.
9. MUST один раз предложить создать **workspace rule / local trust** в `.clinerules/{project-name}.md` для нового проекта, если проект будет накапливать локальный trust-контекст, артефакты, continuity или project-specific knowledge. Если такого файла ещё нет, MUST явно предложить его создать.
10. При Supabase — MUST проверить `.env` на `SUPABASE_URL` и `SUPABASE_ANON_KEY`.

## Project header / project identity
- В первом содержательном ответе нового task, resume, audit, status update или после compaction MUST сначала писать строку `Проект: ...`, а сразу под ней — progress bar Variant 3: `Завершённость: [███████████░░░] 80% — <короткая фаза>`, и только потом основной отчёт.
- Если существует workspace rule `.clinerules/{project-name}.md`, имя этого файла SHOULD быть каноническим project label.
- Если workspace rule отсутствует, агент MUST явно предложить создать его и до этого использовать временный project label, не теряя фокус на проекте.
- `implementation_plan.md`, `cline_docs/project-state.md`, `cline_docs/handoff-summary.md`, handoff / summary / resume docs SHOULD иметь вверху единый project block: строку `Проект: ...`, затем строку `Завершённость: [███████████░░░] 80% — <короткая фаза>`.
- При обновлении continuity-документов агент MUST сохранять этот project block и обновлять вместе с остальным статусом не только имя проекта, но и текстовый progress bar / фазу.
- Для project status/update/planning ответов после project block MUST использовать 3 слоя: `Что строим глобально` → `Средний план` → `Чек-лист`.
- В слое `Что строим глобально` MUST кратко фиксировать конечную цель проекта; если цель ещё не определена, агент MUST сначала предложить и согласовать её с пользователем.
- В слое `Средний план` MUST кратко описывать текущий блок / фазу: что именно делаем сейчас.
- В слое `Чек-лист` MUST давать декомпозицию ближайших исполнимых действий в формате Markdown checklist, пригодном для Cline.

## Project progress bar standard
- Канонический визуальный формат после строки `Проект: ...` = Variant 3: `Завершённость: [███████████░░░] 80% — <короткая фаза>`.
- Процент может быть приблизительным инженерным ориентиром, а не псевдо-точной метрикой; он должен честно отражать стадию проекта.
- Короткая фаза после процента должна описывать текущий этап в 2–5 словах: например `runtime integration`, `regression`, `handoff cleanup`, `planning`.
- Если проект только начат, допустимы низкие значения вроде `10–20%`; если идёт финализация, допустимы `80–95%`; не ставить `100%`, пока definition of done реально не закрыт.

## Workspace rule / local trust
- Для нового проекта MUST один раз предложить создать workspace rule / local trust в `.clinerules/{project-name}.md`.
- Такой файл SHOULD хранить:
  - имя проекта;
  - цель и краткую архитектурную рамку;
  - что уже подтверждено live;
  - ключевые артефакты и где они лежат;
  - continuity docs и порядок чтения для следующей сессии;
  - ограничения, risks и what-is-not-confirmed.
- Workspace rule / local trust = локальный source of truth по проекту и trust-layer внутри workspace.
- Он дополняет `implementation_plan.md`, `cline_docs/project-state.md` и `cline_docs/handoff-summary.md`, а не заменяет их.

## При продолжении проекта
1. MUST прочитать `memory-bank/activeContext.md` и `memory-bank/progress.md`, если папка существует.
2. MUST прочитать `implementation_plan.md` или другой канонический plan file, если задача длинная / многоэтапная.
3. MUST прочитать `cline_docs/project-state.md`, если файл существует.
4. SHOULD читать `cline_docs/handoff-summary.md`, если файл существует и задача длинная / многоэтапная.
5. SHOULD проверить `git status` перед началом изменений.
6. MUST продолжить с того места, где работа была остановлена.
7. SHOULD продолжать работу короткими исполнимыми slices, а не одной длинной фазой без checkpoints.

## Трёхслойное планирование проекта
- Для нетривиальных проектных задач MUST строить план в 3 горизонта:
  1. **Глобальный план** — `implementation_plan.md`, `docs/plan.md` или аналогичный plan file.
  2. **Средний план** — `cline_docs/project-state.md`.
  3. **Точечный чек-лист** — `task_progress`.
- **Глобальный план** MUST описывать цель, scope / non-scope, текущее состояние, ограничения, фазы, зависимости, критерии готовности и риски.
- **Средний план** MUST описывать текущую фазу: входное состояние, 3–7 подэтапов, проверку, выходное состояние и следующий точный шаг.
- **Точечный чек-лист** MUST содержать только ближайший исполнимый slice; обычно 3–6 пунктов достаточно.
- MUST не смешивать уровни: master plan не превращать в микро-чек-лист, а `task_progress` не использовать как master checklist всего проекта.
- SHOULD сначала делать deep-planning для задач с архитектурой, несколькими файлами, несколькими фазами или высоким риском, а затем переводить результат в канонические plan/state файлы.
- SHOULD описывать фазы через deliverables и definition of done, а не через список файлов, которые нужно открыть.
- Глобальный план SHOULD обновляться только при изменении стратегии, scope, зависимостей или definition of done.
- Средний план SHOULD обновляться после значимого slice, смены фазы, перед handoff и перед длинной паузой.
- Для маленьких задач допустимо обойтись средним планом + `task_progress` без отдельного master plan.

## Документация проекта
- Для длинных execution-фаз `cline_docs/handoff-summary.md` SHOULD служить короткой handoff-выжимкой: что подтверждено, что изменено в последней итерации, следующий точный шаг.
- После завершения значимого slice SHOULD обновлять `project-state.md` и `handoff-summary.md` вместе: первый как operational source of truth, второй как быстрый resume-layer.
- Для длинных задач canonical planning split такой:
  - `implementation_plan.md` — глобальный master plan;
  - `cline_docs/project-state.md` — средний operational plan текущей фазы;
  - `task_progress` — точечный checklist текущего исполнимого slice.
- `implementation_plan.md` SHOULD фиксировать фазы, зависимости, definition of done и risks, а не список микро-действий.
- `project-state.md` SHOULD фиксировать текущую фазу, что уже подтверждено, что ещё не подтверждено, следующий точный шаг, modified files, ключевые решения и blockers.

- Репозиторий — основной источник проектных инструкций, архитектурных решений и рабочих команд.
- Документируй значимые изменения поведения, API, архитектуры, инфраструктуры и workflow.
- НЕ создавай отдельную документацию для мелких правок и локальных багфиксов.
- `README.md` — для пользователей и быстрого старта.
- `docs/project.md` и `docs/features/*.md` — для детальной проектной документации.
- Документацию пиши на русском языке.
- Никогда не храни секреты в документации.

## Работа с Git

- Делай commit после завершённого рабочего изменения, которое уже можно проверить, восстановить и review-ить.
- Для длинных задач делай meaningful checkpoints, а не коммит после каждой микроправки.
- Если diff стал слишком большим, рискованным или плохо reviewable, дроби задачу на меньшие части.
- Используй понятные сообщения коммитов на русском.
- Никогда не коммить секреты и `.env` файлы.
- При откате сначала смотри `git log`, затем выбирай точечный `git checkout <commit>` или другой безопасный способ восстановления.

## Skills и project routing
- Для крупных задач и проектной декомпозиции используй skill `epic-planner`.
- Для деплоя и инфраструктурных задач используй `deployment-guide`, а затем профильный deployment skill по платформе.
- Для Railway используй `railway-deploy`, для Render — `render-deploy`, для Vercel — `vercel-deploy`, для VPS/Hostinger — `hostinger-vps`.
- Для больших исследовательских задач по проекту используй `parallel-work`.
- Для задач с Supabase используй `supabase-integration`.
- Для Obsidian-based второго мозга, LLM wiki и knowledge vault используй `obsidian-second-brain`.
