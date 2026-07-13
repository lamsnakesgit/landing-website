Проект: n8-assistant-v2.md
Завершённость: [██████░░░░░░░░░] 40% — carousel MVP

# N8 Assistant v2 — project local rules

## Project identity

- Рабочий продукт: Telegram Mini App / web assistant для AI-задач и автоматизаций.
- Текущая фаза: ранний MVP, Supabase ещё не является полностью готовым production storage.
- Для быстрых продуктовых проверок допустимы local-first HTML-прототипы в `public/carousels/`.

## Carousel branding rule

Для HTML-каруселей, экспортируемых в PNG/Instagram-style assets, по умолчанию добавляй мягкий watermark/brand layer:

- `@lamanopro_ × @aiconicvibe`
- визуальная синяя verified-галочка в стиле Instagram, без использования чужих official assets;
- контакт/канал добавлять только если он нужен в конкретной карусели;
- watermark должен быть читаемым, но не конкурировать с главным контентом;
- watermark размещать в безопасной зоне, обычно bottom-right или footer-zone;
- не добавлять реальные official Instagram logos/trademarks, если пользователь явно не просит и нет прав.

## Carousel layout rule

- Design/export target для Instagram 4:5: `1080×1350`.
- Preview на экране можно уменьшать, но export dimensions не ломать.
- Текст должен помещаться внутри карточек без обрезки.
- Для HTML-прототипов сначала проверять 2 режима:
  - screen preview;
  - export/print layout.
- Если текст не помещается, сначала уменьшать typography scale, padding и density, а не расширять карточку за safe zone.
- Watermark не должен перекрывать footer/copy: либо резервировать место под него, либо делать его частью footer-zone.

## Viral carousel storytelling rule

Перед генерацией карусели обязательно сначала продумывай структуру как связный mini-story, а не набор разрозненных слайдов:

1. **Hook / pattern interrupt** — первый слайд должен выделяться в ленте рекомендаций среди 12–16 соседних постов: крупная провокационная мысль, контраст, обещание или напряжение.
2. **Problem / tension** — быстро назвать боль или парадокс, чтобы человек понял «это про меня».
3. **Reframe / insight** — дать новый взгляд, ради которого стоит листать дальше.
4. **Mechanism** — показать простую модель, формулу, шаги или причину, почему это работает.
5. **Proof / examples** — добавить числа, ситуации, social proof, sold-out, before/after или микро-кейс.
6. **Action / checklist** — дать применимые действия, а не только идею.
7. **CTA / save/share** — завершить конкретным действием: сохранить, написать, перейти, вступить в waitlist.

Копирайтинг и визуализация должны идти вместе:

- 1 слайд = 1 главная мысль;
- заголовок читается за 1–2 секунды;
- каждый следующий слайд отвечает на вопрос, который возник на предыдущем;
- визуал должен усиливать смысл: контраст, стрелки, формулы, числа, ограниченные места, таймер, waitlist, sold out;
- не делать «красиво ради красиво» — каждый визуальный элемент должен помогать дочитать карусель.

## External MiMo subagent rule

Для экономии дорогих токенов Cline/Claude на рутинных задачах по этому проекту можно использовать внешний read-only subagent через локальный `opencode` и бесплатную модель MiMo:

```bash
opencode run -m opencode/mimo-v2.5-free '...задача...'
```

Использовать MiMo в первую очередь для:

- первичного анализа файлов и логов;
- поиска гипотез по багам;
- генерации черновиков, вариантов текста и boilerplate;
- сравнения простых подходов;
- подготовки краткого JSON-резюме для последующего решения в Cline.

Ограничения:

- MiMo external subagent не заменяет встроенный `use_subagents` Cline и не управляет его моделью;
- по умолчанию давать MiMo read-only контракт: `ничего не меняй`, `не запускай destructive commands`, `верни краткий JSON`;
- финальные правки, архитектурные решения, security-sensitive действия и production-fixes проверяет и выполняет Cline/Claude;
- если MiMo зависает дольше 30–60 секунд, читать background log и при необходимости останавливать процесс `pkill -f "opencode run -m opencode/mimo-v2.5-free"`.

Проверенный smoke-test:

```bash
opencode run -m opencode/mimo-v2.5-free 'Ответь одной строкой JSON: {"ok":true,"model":"mimo"}. Не читай файлы и ничего не меняй.'
```

Ожидаемый ответ:

```json
{"ok":true,"model":"mimo"}
```

## Current carousel artifact

- `n8-assistant-v2/public/carousels/hormozi-offers-carousel.html`
- Название: `Формула дорогого оффера`
- Тема: заметки по `$100M Offers` / офферы, scarcity, urgency, bonuses, FOMO.
