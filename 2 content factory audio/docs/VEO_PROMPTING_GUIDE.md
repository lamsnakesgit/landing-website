# Гайд по промптам для Veo 3.1
# Veo 3.1 Prompting Guide (Expert Edition)

Этот гайд поможет вам создавать идеальные промпты для генерации видео с аватарами, которые выглядят профессионально и не блокируются фильтрами Google.

## 📐 Золотая формула промпта
Для достижения 4K качества и плавности, ваш промпт должен выглядеть так:

> **[Камера] + [Объект из фото] + [Действие и речь] + [Окружение] + [Свет] + [Качество]**

### Пример идеального промпта:
`Cinematic close-up of a professional woman from the reference photo, she is talking naturally to the camera in Russian about AI business solutions, her facial expressions are natural, professional office background with bokeh effect, shot on 35mm lens, corporate lighting, 4k high-resolution.`

---

## 🚫 Что НЕЛЬЗЯ делать (Чтобы не было блока)
1. **Не используйте слова-триггеры:** `Deepfake`, `Fake`, `Manipulated`, `Mimic`.
2. **Не приказывайте жестко:** Вместо `I want her to scream words X`, используйте `She is expressively speaking in a loud tone about X`.
3. **Не забывайте про референс:** Всегда упоминайте, что объект должен соответствовать фото: `woman from the reference image`.

## 🎨 Тюнинг параметров
- **Aspect Ratio**: `9:16` (для Reels/Shorts), `16:9` (для YouTube).
- **Style**: Если хотите «премиум» стиль, добавьте: `Sleek corporate aesthetics, vibrant 4k colors, crisp textures`.
- **Speech**: Если нужно видео с речью, всегда используйте модель `veo-3.1-generate-preview`.

## 🛠 Коды для копирования (Cheat Sheet)
- **Zoom**: `Slow dolly-in zoom towards the subject face`.
- **Handheld**: `Subtle handheld camera movement for documentary feel`.
- **Office**: `Modern high-tech headquarters with glass walls and sunset light`.
- **Russian Speech**: `The character speaks clearly in Russian with accurate lip-syncing`.
