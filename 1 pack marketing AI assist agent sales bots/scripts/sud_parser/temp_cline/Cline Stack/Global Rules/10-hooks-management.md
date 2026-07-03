# Управление хуками (Hooks Management)

> 📁 Полная документация, шаблоны и примеры — в скилле `hooks-management`.
> MUST использовать `use_skill("hooks-management")` при создании или отладке хуков.

## Расположение
- **Глобальные**: `~/Documents/Cline/Hooks/` — для всех проектов
- **Проектные**: `.clinerules/hooks/` — только для конкретного проекта

## Установленные хуки

| Хук | Назначение |
|---|---|
| `TaskStart` | Логирует начало задачи, добавляет timestamp в контекст |
| `TaskComplete` | Отправляет уведомление в Telegram |
| `PreToolUse` | Блокирует .js в TS-проектах, защищает от `rm -rf /`, блокирует `git add .env` |
| `PostToolUse` | Логирует метрики в `~/Documents/Cline/Logs/tool-usage.log` |

## Когда использовать hooks
- Используй hooks для детерминированной автоматизации, валидации, policy enforcement и логирования.
- Используй hooks, когда действие должно происходить автоматически и без пропусков.
- Не используй hooks для гибкой логики, длинных рассуждений или редких workflow — для этого есть rules, skills и workflows.

## Базовые правила
- MUST возвращать валидный JSON в stdout.
- MUST логировать в stderr (`>&2`), не в stdout.
- SHOULD делать hooks быстрыми, минимальными и предсказуемыми.
- NEVER блокировать операции без веской причины, особенно в `PreToolUse`.
- Для сложной логики hook-ов, шаблонов и debugging используй skill `hooks-management`.

## Границы и ограничения
- Hooks — это enforcement layer, а не замена rules, skills и workflows.
- Блокирующие hooks должны срабатывать только на high-confidence и high-risk случаях.
- Если hook начинает мешать обычной работе чаще, чем предотвращает реальную проблему, его нужно упростить или пересмотреть.
- `Notification` не работает в VS Code — используй `Stop` там, где нужна реакция по завершению.

## Routing note для context / continuity hooks
- Для context/continuity hook architecture source of truth должен жить не только в самом hook-коде, но и в runbook / workspace note.
- Если hooks обслуживают continuity, telemetry и compaction recovery, держи краткий summary в workspace note, а подробную operational схему — в runbook.
- Если рабочая hook-система ушла дальше общего правила, обнови routing note или ссылку на runbook, чтобы Rules не отставали от runtime.
