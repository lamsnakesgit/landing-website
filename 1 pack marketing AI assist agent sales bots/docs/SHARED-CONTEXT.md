# Shared Context: Cline + AntiGravity Bots

## Архитектура

```
┌────────────────────────────────────────────────────────────┐
│                    ~/.agents/skills/                        │
│               (Глобальные skills — общие)                   │
│  source-code-context  code-structure-cleanup                │
│  workflow-research    workflow-sales                        │
│  telegram             telegram-voice-briefing               │
│  b2b-lead-enricher    ...                                   │
└────────────────────┬───────────────────────────────────────┘
                     │ читают
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│  Cline   │  │ Cline    │  │  AntiGravity │
│ (main)   │  │ (task)   │  │  Telegram    │
└────┬─────┘  └────┬─────┘  └──────┬───────┘
     │             │               │
     └─────────────┼───────────────┘
                   ▼
        ┌──────────────────┐
        │  AGENTS.md        │ ← единый источник для всех
        │  docs/SHARED-     │
        │  CONTEXT.md       │
        └──────────────────┘
```

## Как это работает

### 1. Глобальные skills (`~/.agents/skills/`)
- Доступны ВСЕМ инстансам Cline и AntiGravity
- Source of truth: физические файлы на диске
- Не дублировать в workspace

### 2. Workspace skills (`.agents/skills/`)
- Специфичные для проекта
- Для этого репозитория: sales-team, b2b-lead-enricher, code-structure-cleanup
- Могут ссылаться на глобальные

### 3. AGENTS.md
- Единый routing для всех агентов
- Содержит: какие skills есть, где лежат скрипты, интеграции
- Cline читает напрямую, AntiGravity — через shared path

### 4. Communication (agent → agent)
- Через файлы: `docs/SHARED-CONTEXT.md`, `docs/PROGRESS.md`
- Через Telegram: AntiGravity бот может триггерить Cline через n8n webhook
- Через n8n: общий workflow для обоих агентов

## Как не мешать друг другу

1. **Cline** — разработка, код, архитектура, деплой
2. **AntiGravity** — уведомления, мониторинг, пользовательский интерфейс в Telegram
3. **Конфликт**: если оба агента пишут в один файл → использовать блокировку через `lock file`
4. **Параллельная работа**: `git worktree` для изолированных веток

## Worktree (когда нужен)

- Когда 2+ агента работают над разными фичами в одном репозитории
- Каждый агент в своей ветке → свой worktree
- Не нужен для read-only работы или последовательных задач

## Что делать если агенты конфликтуют

1. Проверить `docs/SHARED-CONTEXT.md`
2. Проверить `docs/BLOCKERS.md`
3. Запустить `/newtask` для очистки контекста
4. Если автономно не решается — пинг через Telegram