# Cline Stack

## Что это
Это экспорт **global Cline stack** для передачи ученикам и установки на **macOS** или Аналогов для Windows:
- Global Rules
- Global Hooks
- Global Skills

Да, по-английски **stack** — это правильное слово.

Сборка подготовлена из рабочего окружения **Mac + VS Code + Cline**.
Для **Windows** совместимость не гарантируется без адаптации путей, shell-скриптов, хуков и локальной структуры каталогов.

## Что внутри
- `Global Rules/` — глобальные правила Cline
- `Global Hooks/` — глобальные хуки Cline
- `Global Skills/` — глобальные skills Cline
- `PROMPT_FOR_STUDENTS_CLINE.txt` — готовый текст для ученика или его Cline-агента
- `manifest.json` — сводка по экспорту и проверке

## Важно
- Это **экспортная версия для передачи**.
- Локальный Cline на этом Mac **не менялся**.
- Чувствительные токены/секреты очищены.
- Персональные IP, домены, SSH-команды, пути и инфраструктурные адреса заменены на **примеры** и placeholders вида `<YOUR_...>`.
- Если ученику или его ИИ-агенту нужны реальные данные, агент должен **подставить реальные данные пользователя** или **спросить их у пользователя**.
- Project-specific `.clinerules/` в экспорт **не включались**.

## Куда устанавливать на macOS
### Global Rules
`/Users/<ВАШ_ПОЛЬЗОВАТЕЛЬ>/Documents/Cline/Rules`

### Global Hooks
`/Users/<ВАШ_ПОЛЬЗОВАТЕЛЬ>/Documents/Cline/Hooks`

### Global Skills
`/Users/<ВАШ_ПОЛЬЗОВАТЕЛЬ>/.agents/skills`

## Что экспортировано из Global Rules
- 01-language-and-style.md
- 02-documentation-search.md
- 03-context-memory-bank.md
- 04-web-development.md
- 05-search-tools.md
- 06-code-quality.md
- 07-project-workflow.md
- 08-tool-usage.md
- 09-skills-management.md
- 10-hooks-management.md
- 11-browser-automation.md
- 12-headless-mode.md
- 13-parallel-work.md
- 14-telegram-integration.md
- 15-plan-mode-limitations.md
- 16-ai-agent-collaboration.md
- 17-obsidian-second-brain.md
- tech-stack.md
- USER.md

## Как установить вручную
1. Закрой VS Code / Cline.
2. Скопируй содержимое `Global Rules/` в `~/Documents/Cline/Rules`.
3. Скопируй содержимое `Global Hooks/` в `~/Documents/Cline/Hooks`.
4. Скопируй содержимое `Global Skills/` в `~/.agents/skills`.
5. Запусти VS Code / Cline заново.

## Что сказать ученикам / их ИИ-агенту Cline
Можно передать файл `PROMPT_FOR_STUDENTS_CLINE.txt`.

Короткая версия:
- установить `Global Rules` в `~/Documents/Cline/Rules`
- установить `Global Hooks` в `~/Documents/Cline/Hooks`
- установить `Global Skills` в `~/.agents/skills`
- если чего-то не хватает — создать
- перед заменой файлов предупредить или сделать backup
- не трогать project-specific `.clinerules/`
- после установки проверить структуру
- если в skill/documentation встречаются placeholders `<YOUR_...>`, агент должен подставить реальные данные пользователя или сначала спросить их у пользователя

## Техническая пометка
Дата экспорта: 2026-04-27 09:50:07
Источник: macOS / VS Code / Cline
