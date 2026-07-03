# Управление навыками (Skills Management)

## Правила использования Skills
- MUST проверять доступные skills перед сложной задачей.
- MUST использовать `use_skill()`, когда задача явно соответствует существующему skill.
- NEVER угадывать syntax, API или workflow, если есть релевантный skill.
- Глобальные Skills: `~/.agents/skills/`
- Проектные Skills: `.agents/skills/` внутри проекта

## Когда использовать skill
- Когда нужна специализированная domain-логика, которая не должна быть always-on.
- Когда задача требует повторяемого workflow, сложной процедуры или глубоких best practices.
- Когда подробные инструкции, примеры или scripts были бы слишком тяжёлыми для rules.

## Когда НЕ использовать skill
- Когда правило должно работать всегда и относится к базовому поведению агента.
- Когда задача слишком мала, чтобы загружать отдельный skill.
- Когда достаточно existing rule, workflow или hook без дополнительного on-demand слоя.
- Не создавай skill для единичной случайной ситуации без повторяющегося паттерна.

## Как выбирать слой
- **Rules** — always-on guidance, базовые ограничения, поведение и стандарты.
- **Skills** — on-demand экспертиза, глубокие workflow, best practices, references и scripts.
- **Workflows** — явные повторяемые последовательности действий, запускаемые вручную.
- **Hooks** — детерминированная автоматизация и enforcement в lifecycle-событиях.

## Формат файла SKILL.md
- Каждый skill MUST начинаться с YAML frontmatter.
- Минимум: `name` и `description`.
- Для сложных skills SHOULD использовать `examples/`, `templates/`, `scripts/` или дополнительные docs.
- Skill должен быть коротким в ядре и грузить детали по ссылкам или через bundled files.

## Skills routing

| Skill | Когда использовать |
|---|---|
| `browser-automation` | Playwright, браузер, клики, скриншоты, e2e тесты |
| `connect-automation` | N8N, webhooks, HTTP, error handling |
| `n8n-expressions` | Выражения `{{ }}`, `$json`, `$node`, `$env` |
| `n8n-workflow-patterns` | Выбор архитектуры workflow |
| `n8n-workflow-implementation` | Создание workflows с 15+ нодами через API |
| `n8n-validation` | Ошибки `validate_node`, `validate_workflow` |
| `n8n-code-javascript` | JavaScript в Code node |
| `n8n-executions-debug` | Диагностика failed executions |
| `n8n-http-request` | HTTP Request node, auth, pagination |
| `n8n-ai-agent-patterns` | AI Agent workflows, tools, memory |
| `deployment-guide` | Выбор платформы, деплой |
| `hostinger-vps` | VPS, SSH, Docker, Hostinger |
| `vercel-deploy` | Vercel, Next.js, React |
| `railway-deploy` | Railway, БД, воркеры |
| `render-deploy` | Render, API серверы |
| `supabase-integration` | Supabase, Auth, RLS, Storage |
| `telegram` | Telegram Bot API, уведомления |
| `telegram-mini-apps` | TMA, TON, бот |
| `telegram-initdata-validation` | Валидация initData |
| `frontend-design` | React, Tailwind, product UI, responsive components, accessible forms/widgets, state-complete app surfaces |
| `cc-design` | General-purpose HTML-first high-fidelity design, prototypes, slide decks, landing pages, design systems, verification-first workflow, app/prototype guardrails |
| `huashu-design` | HTML-first high-fidelity prototypes, interactive demos, slide decks, motion design, design variations, MP4/GIF/PPTX export, asset-driven workflows, expert design review |
| `implementation-research` | Готовые реализации, mature patterns, repo examples, external implementation research |
| `hooks-management` | Cline Hooks, bash-скрипты |
| `headless-mode` | Cline CLI на VPS, cron |
| `parallel-work` | Sub-агенты, git worktrees |
| `epic-planner` | Декомпозиция крупных задач |
| `systematic-debugging` | Системная отладка сложных багов |
| `local-code-search` | Семантический поиск по репозиторию |
| `notion-integration` | Notion API |
| `owasp-security` | Безопасность веб-приложений |
| `transcript-analyzer` | Транскрипты YouTube/аудио |
| `langsmith-fetch` | LangSmith трассировка LLM |
| `kie-ai-integration` | kie.ai API (изображения, видео, аудио) |
| `obsidian-second-brain` | Obsidian second brain / LLM wiki, vault scaffold, hot cache, index/log structure |
| `obsidian-second-brain-ingest` | Ingest новых источников в Obsidian vault |
| `obsidian-second-brain-save` | Save-back ценных результатов сессии в Obsidian vault |
| `obsidian-second-brain-lint` | Аудит и health check Obsidian vault |
| `obsidian-second-brain-world` | Быстрое восстановление рабочего контекста из Obsidian vault |

## Registry discipline
- Rules routing MUST ссылаться только на skills, доступные в активном system registry, а не просто существующие на диске.
- Если skill-папка есть в `~/.agents/skills/`, но skill отсутствует в текущем system registry, такой skill считается **local-only / unregistered** и не должен быть обязательной точкой routing в global rules.
- Если UI-задача затрагивает кастомные виджеты, keyboard/focus behavior, forms или accessibility, routing должен вести не только в UI skill, но и к official accessibility/pattern docs, а не к импровизации «по памяти».
- Для query-задач по Obsidian vault canonical routing сейчас: `obsidian-second-brain` + при необходимости `obsidian-second-brain-world`.
- Перед переводом local-only skill в общий routing нужно синхронизировать три слоя: папка skill → Rules routing → system registry.
- Локальные skill-папки `gemini-embedding-2-preview`, `supabase-gemini-rag`, `supabase-mcp`, `obsidian-second-brain-query` пока нельзя считать частью глобально доступного routing, пока они не добавлены в registry.

## Создание нового Skill
- Предлагай новый skill, если паттерн повторяется 3+ раза и не должен жить в always-on rules.
- Перед созданием нового skill проверь, не покрывается ли задача существующим skill, workflow или hook.
- Новый skill должен давать реальную повторяемую ценность: domain depth, workflow, patterns, scripts или проверяемые примеры.
- Файл: `~/.agents/skills/<skill-name>/SKILL.md`
- Перед добавлением нового skill согласуй это с пользователем.
- Для создания, обновления и оценки новых skills используй skill `skill-authoring`, если задача именно про authoring/evolution skills.

## Эволюция системы через Rules + Skills
- Если найден повторяемый и устойчивый паттерн, агент SHOULD оценить, где он должен жить: Rule, Skill, Hook, Workflow или project note.
- NEVER создавать новый skill только потому, что произошла одна случайная ошибка или был один единичный кейс.
- Новые skills должны появляться через осознанный отбор, а не через хаотичное накопление знаний.
- Если создаётся новый skill, проверь, нужен ли короткий routing update в Rules, чтобы Rules и Skills не расходились.
- Если после ошибки или неудачного решения появился **проверенный и повторяемый урок**, сначала классифицируй его как Rule / Skill / Hook / Workflow / project note и только потом создавай новый артефакт.
- Если lesson candidate тянет на новый или обновлённый skill, SHOULD использовать `skill-authoring` как канонический процесс authoring/evolution.
