---
name: obsidian-second-brain-save
description: Use when a conversation or result produced reusable knowledge that should be filed back into the Obsidian second brain as questions, comparisons, updated entities/concepts, and refreshed hot/focus state.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Obsidian Second Brain Save

Сохраняй действительно ценные результаты сессии обратно в vault, чтобы знания компаундились.

## Когда использовать
- пользователь говорит «сохрани это в brain / vault / wiki»;
- query дал полезное сравнение, synthesis или вывод;
- в сессии приняты решения, которые должны остаться в knowledge base;
- нужно разложить итог разговора по существующим wiki-страницам;
- живая аналитическая сессия дала decision-ready answer, который стоит повторно использовать.

## Когда НЕ использовать
- сессия не дала нового знания;
- это одноразовый ответ, который не стоит хранить;
- сначала нужно ingest-нуть новый источник;
- у тебя только сырой transcript без нормального verdict / synthesis.

## Типы save-back артефактов
Выбери **один главный тип** результата:

1. **Question save**
   - куда: `wiki/questions/`
   - когда: ответ на вопрос получился сильным и его вероятно спросят ещё раз
2. **Comparison save**
   - куда: `wiki/comparisons/`
   - когда: есть сравнение вариантов, trade-offs, verdict
3. **Entity update**
   - куда: `wiki/entities/`
   - когда: сессия добавила новые факты о человеке/компании/продукте/репозитории
4. **Concept update**
   - куда: `wiki/concepts/`
   - когда: сессия уточнила идею, паттерн, метод или framework
5. **Focus shift**
   - куда: `wiki/meta/current-focus.md`
   - когда: реально поменялись активные knowledge priorities

## Workflow
1. Определи, что именно является vault-worthy: question answer, comparison, concept update, entity update, new focus shift.
2. Сначала поищи существующие страницы, которые нужно обновить.
3. Если нужен новый артефакт, выбери правильное место: `wiki/questions/`, `wiki/comparisons/`, `wiki/entities/`, `wiki/concepts/`.
4. Используй соответствующий template как стартовую форму, а не пиши страницу с нуля без структуры.
5. Запиши результат кратко и структурированно, с `[[wikilinks]]` на supporting pages.
6. Для `question` и `comparison` страниц добавляй не только ответ, но и supporting pages / follow-up angles.
7. Для `entity` и `concept` updates предпочитай дописывать существующие разделы, а не плодить новые похожие страницы.
8. Обнови `wiki/index.md`.
9. Добавь запись в `wiki/log.md` с коротким summary what/where/why.
10. Обнови `wiki/hot.md`.
11. Если изменился активный фокус, обнови `wiki/meta/current-focus.md`.
12. При крупных save-back операциях используй `wiki/meta/save-report-template.md` как формат артефакта.

## Live session pattern
Нормальный save-back после реальной аналитической сессии обычно выглядит так:
- **1 главный artifact**: question или comparison page с reusable answer;
- **1–2 supporting updates**: concept/framework/comparison update;
- **continuity refresh**: `index.md`, `log.md`, `hot.md`, при необходимости `current-focus.md`;
- **cleanup**: если сессия вскрыла stale references или вымышленные страницы, сначала приведи live layer в честное состояние.

Не пытайся делать из каждой сессии мини-энциклопедию. Цель — сохранить минимальный, но сильный набор reusable артефактов.

## Save-back contract
Сохраняй только то, что проходит минимум 2 из 3 критериев:
- **reusable** — это пригодится позже;
- **specific** — есть конкретные факты, вывод, сравнение или решение;
- **linked** — можно связать с существующими страницами через `[[wikilinks]]`.

Если результат не проходит этот порог — **не сохраняй**.

## Логирование
Минимальная запись в `wiki/log.md` должна отвечать на 3 вопроса:
- что сохранили;
- куда сохранили;
- почему это важно.

Для крупных save-back операций используй `wiki/meta/save-report-template.md`.

## Практические правила
- не всё из беседы достойно сохранения;
- prefer update existing over creating duplicate synthesis pages;
- save-back должен быть коротким, полезным и переиспользуемым;
- если результат слабый, лучше не сохранять его вовсе;
- не превращай save-back в сырой transcript dump;
- если knowledge layer уже ушёл в drift, cleanup перед refresh continuity важнее cosmetic expansions.

## Smoke tests
- «Сохрани это сравнение в мой второй мозг» → создаётся page в `wiki/comparisons/`, обновляются index/log/hot.
- «Сохрани ответ на этот вопрос в vault» → создаётся page в `wiki/questions/` или обновляется существующая.
- «Обнови мои заметки по этой концепции на основе разговора» → обновляется `wiki/concepts/...` вместо создания дубля.
- «Сохрани живую аналитическую сессию по pricing» → появляется 1 главный артефакт, supporting updates, continuity refresh и при необходимости cleanup stale refs.

## Red flags
- сохранять шумные промежуточные мысли;
- плодить новые страницы вместо обновления существующих;
- забыть обновить `hot.md` и `log.md` после save-back;
- сохранять raw transcript вместо knowledge artifact;
- маскировать рассинхрон knowledge layer созданием новых страниц поверх drift.
