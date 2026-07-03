# Obsidian Second Brain — Safe Fix Policy

## Цель
Определить, что можно чинить автоматически в vault, а что требует подтверждения пользователя.

## Safe auto-fix
Разрешено чинить автоматически:
- missing index entry при однозначной категории;
- очевидный broken wikilink при однозначном target;
- создание report files в `wiki/meta/`;
- минимальное заполнение frontmatter при детерминированных значениях.

## Confirm-first changes
Требуют подтверждения:
- удаление или merge страниц;
- массовое переписывание cross-links;
- исправление знаний, где есть конкурирующие трактовки;
- спорные stale claims;
- любые structural changes, затрагивающие несколько разделов vault.

## Never auto-fix
Никогда не чини автоматически:
- raw source content;
- knowledge conflicts, где нужно содержательное решение;
- current focus, если это требует интерпретации приоритетов пользователя;
- save-back decisions без достаточной уверенности, что это reusable knowledge.
