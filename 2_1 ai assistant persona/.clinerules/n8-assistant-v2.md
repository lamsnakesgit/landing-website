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
- `t.me/nnsvt` как компактный контакт/канал;
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

## Current carousel artifact

- `n8-assistant-v2/public/carousels/hormozi-offers-carousel.html`
- Название: `Формула дорогого оффера`
- Тема: заметки по `$100M Offers` / офферы, scarcity, urgency, bonuses, FOMO.