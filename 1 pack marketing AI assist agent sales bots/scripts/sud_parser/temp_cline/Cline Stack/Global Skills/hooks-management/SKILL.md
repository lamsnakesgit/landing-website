---
name: hooks-management
description: Создание и управление Cline Hooks — bash-скрипты для валидации операций, логирования метрик, инъекции контекста и уведомлений. Используй при создании, отладке или настройке хуков.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Hooks Management

## Расположение

- **Глобальные**: `~/Documents/Cline/Hooks/` — для всех проектов
- **Проектные**: `.clinerules/hooks/` — только для конкретного проекта

## Типы хуков

| Хук | Когда срабатывает |
|---|---|
| `TaskStart` | Начало новой задачи |
| `TaskResume` | Возобновление задачи |
| `TaskCancel` | Отмена задачи |
| `TaskComplete` | Завершение задачи |
| `PreToolUse` | Перед выполнением инструмента |
| `PostToolUse` | После выполнения инструмента |
| `UserPromptSubmit` | Отправка сообщения пользователем |
| `PreCompact` | Перед сжатием контекста |

## Формат скрипта

### Input (JSON через stdin)
```json
{
  "taskId": "abc123",
  "clineVersion": "3.36.0",
  "timestamp": 1736654400000,
  "workspacePath": "/path/to/project",
  "hookSpecificField": {}
}
```

### Output (JSON в stdout)
```json
{
  "cancel": false,
  "contextModification": "Текст добавляется в следующий запрос к LLM",
  "errorMessage": ""
}
```

### Шаблон нового хука
```bash
#!/bin/bash
INPUT=$(cat)

if ! command -v jq &> /dev/null; then
  echo '{"cancel":false}'
  exit 0
fi

TOOL=$(echo "$INPUT" | jq -r '.preToolUse.tool // ""')

# Логика здесь
echo '{"cancel":false}'
```

## Ключевые возможности

### Блокировка операции (`cancel: true`)
```bash
echo '{"cancel":true,"errorMessage":"Операция заблокирована: причина"}'
```

### Инъекция контекста
```bash
echo '{"cancel":false,"contextModification":"Примечание: используй TypeScript"}'
```

## Установленные хуки

| Хук | Назначение |
|---|---|
| `TaskStart` | Логирует начало задачи, добавляет timestamp в контекст |
| `TaskComplete` | Отправляет уведомление в Telegram |
| `PreToolUse` | Блокирует .js в TS-проектах, защищает от `rm -rf /`, блокирует `git add .env` |
| `PostToolUse` | Логирует метрики в `~/Documents/Cline/Logs/tool-usage.log` |

## Управление

```bash
# Включить хук
chmod +x ~/Documents/Cline/Hooks/TaskComplete

# Выключить хук
chmod -x ~/Documents/Cline/Hooks/TaskComplete

# Просмотр логов
tail -20 ~/Documents/Cline/Logs/tool-usage.log

# Поиск ошибок
grep "success:false" ~/Documents/Cline/Logs/tool-usage.log
```

## Типы хуков (command, prompt, agent)

| Тип | Когда использовать |
|---|---|
| `command` | Shell-команда, любые автоматизации |
| `prompt` | Простые проверки через Claude Haiku |
| `agent` | Сложные проверки с инструментами |

## Exit-коды

- `0` — успех, продолжаем
- `1` — ошибка, показываем пользователю, продолжаем
- `2` — блок, останавливаем действие (только PreToolUse)

## Хуки внутри скиллов

```yaml
---
name: secure-deploy
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/safety-check.sh"
---
```

## Ограничения в VS Code

`Notification` и `PermissionRequest` не работают в VS Code — используй хук `Stop` вместо `Notification`.

## Правила

- 🚨 MUST использовать `jq` для парсинга JSON, с graceful fallback если недоступен
- 🚨 MUST всегда возвращать валидный JSON в stdout
- MUST логировать в stderr (`>&2`), не в stdout
- SHOULD выполняться быстро (< 5 секунд)
- NEVER блокировать операции без веской причины
- SHOULD использовать `exit 0` после каждого `echo` с JSON