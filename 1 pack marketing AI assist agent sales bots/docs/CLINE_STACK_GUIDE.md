# Cline Stack Guide

## Что это за сущности

### Skills
Skills — это подключаемые экспертные режимы для конкретных типов задач.

Простыми словами:
- если задача про браузер — подключается skill для браузерной автоматизации;
- если задача про деплой — подключается skill по деплою;
- если задача про отладку — подключается skill по системной отладке.

Зачем нужны skills:
- меньше импровизации;
- меньше ошибок;
- быстрее доходить до рабочего результата;
- использовать готовые проверенные workflow под конкретную тему.

### Hooks
Hooks — это автоматические действия до/после событий в работе агента.

Примеры:
- старт задачи;
- завершение задачи;
- перед запуском инструмента;
- после запуска инструмента;
- старт сессии;
- подготовка к compaction.

Зачем нужны hooks:
- автоматическая защита от ошибок;
- логирование;
- восстановление контекста;
- более стабильный и повторяемый процесс работы.

### Rules
Rules — это постоянные правила поведения агента.

Они определяют:
- как писать ответы;
- как писать код;
- как искать документацию;
- как работать с проектами;
- как использовать tools;
- когда использовать skills;
- как вести длинные задачи.

Зачем нужны rules:
- работа становится предсказуемее;
- меньше хаоса;
- выше безопасность;
- легче держать единый стиль и качество.

### Workflows
Workflows — это повторяемые рабочие сценарии.

Например:
- как ставить MCP;
- как делать handoff;
- как выполнять deep planning;
- как проверять деплой;
- как проводить аудит.

Зачем нужны workflows:
- не изобретать один и тот же процесс заново;
- ускорять типовые задачи;
- уменьшать количество пропущенных шагов.

Важно: в найденном архиве отдельного блока `Workflows` не было.

---

## Что установлено сейчас

### 1. Skills
Установлено 50 skills в папку:

`~/Documents/Cline/Skills`

Примеры самых заметных:
- `browser-automation`
- `cc-design`
- `connect-automation`
- `deployment-guide`
- `epic-planner`
- `frontend-design`
- `headless-mode`
- `hooks-management`
- `hostinger-vps`
- `implementation-research`
- `local-code-search`
- `n8n-ai-agent-patterns`
- `n8n-code-javascript`
- `n8n-executions-debug`
- `n8n-expressions`
- `n8n-http-request`
- `n8n-validation`
- `n8n-workflow-implementation`
- `n8n-workflow-patterns`
- `notion-integration`
- `obsidian-second-brain`
- `owasp-security`
- `parallel-work`
- `railway-deploy`
- `render-deploy`
- `supabase-integration`
- `systematic-debugging`
- `telegram`
- `telegram-mini-apps`
- `transcript-analyzer`
- `vercel-deploy`

### 2. Hooks
Установлены hooks в папку:

`~/Documents/Cline/Hooks`

Там есть:
- `TaskStart`
- `TaskComplete`
- `PreToolUse`
- `PostToolUse`
- `SessionStart`
- `PreCompact`
- backup-файлы
- `scripts/`

### 3. Rules
Новые global rules установлены в отдельную папку:

`~/Documents/Cline/Rules/stack_rules_20260515_200631`

Там лежат:
- `01-language-and-style.md`
- `02-documentation-search.md`
- `03-context-memory-bank.md`
- `04-web-development.md`
- `05-search-tools.md`
- `06-code-quality.md`
- `07-project-workflow.md`
- `08-tool-usage.md`
- `09-skills-management.md`
- `10-hooks-management.md`
- `11-browser-automation.md`
- `12-headless-mode.md`
- `13-parallel-work.md`
- `14-telegram-integration.md`
- `15-plan-mode-limitations.md`
- `16-ai-agent-collaboration.md`
- `17-obsidian-second-brain.md`
- `USER.md`
- `tech-stack.md`

### 4. Старые файлы не затёрты
Существующий файл:

`~/Documents/Cline/Rules/cline_rule_.md`

не был удалён.

Перед установкой был создан backup текущего правила.

---

## Что это даёт на практике

### Для разработки
- лучшее следование процессу;
- меньше случайных действий;
- более сильные подсказки по стеку и инфраструктуре;
- готовые режимы для деплоя, отладки, браузера, n8n, Telegram, Supabase.

### Для автоматизации
- можно быстрее строить повторяемые сценарии;
- легче подключать агент к стандартным процессам;
- меньше ручного объяснения одного и того же.

### Для обучения
- это готовая база знаний по тому, как агент должен работать;
- по skills можно учиться, какие режимы уже существуют;
- по rules можно понять, как строится дисциплина работы;
- по hooks можно понять, что именно автоматизируется на уровне процесса.

---

## Самые полезные штуки для твоего стека

Если смотреть именно под твои задачи, самые полезные группы такие:

### Для AI-разработки и кода
- `implementation-research`
- `local-code-search`
- `systematic-debugging`
- `epic-planner`
- `browser-automation`

### Для n8n и автоматизаций
- `connect-automation`
- `n8n-ai-agent-patterns`
- `n8n-http-request`
- `n8n-expressions`
- `n8n-validation`
- `n8n-executions-debug`
- `n8n-workflow-implementation`
- `n8n-workflow-patterns`

### Для инфраструктуры и деплоя
- `deployment-guide`
- `hostinger-vps`
- `railway-deploy`
- `render-deploy`
- `vercel-deploy`
- `headless-mode`

### Для Telegram / Mini Apps
- `telegram`
- `telegram-mini-apps`
- `telegram-initdata-validation`

### Для дизайна и интерфейсов
- `frontend-design`
- `cc-design`
- `huashu-design`

---

## Что стоит понимать дальше

1. Не все установленные skills автоматически активны всегда.
2. Skills подключаются по необходимости.
3. Rules действуют как постоянный базовый слой поведения.
4. Hooks — это слой автоматизации вокруг событий.
5. Workflows — это повторяемые схемы работы, но в этом архиве отдельного workflow-блока не было.

---

## Практические next steps

### Вариант 1 — учебный
Разобрать по очереди:
1. `Rules`
2. `Hooks`
3. топ-10 `Skills`

### Вариант 2 — прикладной
Сразу использовать самые полезные для твоих задач:
- `implementation-research`
- `local-code-search`
- `systematic-debugging`
- `connect-automation`
- `n8n-*`
- `telegram`
- `hostinger-vps`

### Вариант 3 — audit
Сделать отдельный аудит:
- какие hooks реально стоит оставить включёнными;
- какие skills самые полезные именно под твои текущие проекты;
- что лучше отключить, чтобы не усложнять систему.

---

## Короткий вывод

Сейчас у тебя уже есть полноценная база:
- global skills;
- global hooks;
- global rules;
- backup старого правила;
- безопасная установка без удаления существующих файлов.

Это хорошая основа, чтобы дальше:
- быстрее разрабатывать;
- лучше автоматизировать;
- системно обучать агента под твой стиль работы.