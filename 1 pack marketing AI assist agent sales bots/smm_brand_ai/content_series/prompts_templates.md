# Шаблоны промптов для ИИ-сериалов (Сохранение консистентности лица)

В создании ИИ-сериалов ключевая сложность — сделать так, чтобы персонаж на всех кадрах выглядел одинаково. Ниже описаны проверенные техники для генерации стабильных персонажей в Midjourney/Flux и последующей анимации в Luma, Kling, Runway Gen-3 или Google Veo.

---

## 🧑‍🎨 Шаг 1: Создание консистентного персонажа

Чтобы лицо персонажа не менялось от сцены к сцене, используйте следующие подходы:

### Подход А: Использование Midjourney `--cref` (Character Reference)
1. Сгенерируйте стартовое изображение вашего персонажа в хорошем качестве (лицо анфас или три четверти, хорошее освещение).
2. Скопируйте ссылку на полученное изображение (назовем её `CHAR_URL`).
3. Для всех последующих генераций добавляйте в конец промпта параметр `--cref CHAR_URL`.
4. Используйте параметр `--cw` (Character Weight, вес схожести одежды и волос):
   *   `--cw 100` (по умолчанию) — копирует лицо, прическу и одежду (подходит, если персонаж в одной серии одет одинаково).
   *   `--cw 0` — копирует **только лицо** персонажа, позволяя менять ему одежду, позы и прически в разных сценах.

### Подход Б: Текстовый якорь (для Flux и Midjourney)
Опишите персонажа максимально уникально и детально, чтобы нейросеть «запомнила» его черты:
> **Шаблон описания лица:** `A 25-year-old Kazakh guy, sharp jawline, short messy black hair, round black-rimmed glasses, wearing a solid blue hoodie.`

Используйте этот текстовый якорь в начале каждого промпта.

---

## 🎬 Шаг 2: Шаблон промпта для ИИ-сериала

Используйте эту структуру для создания каждой сцены:

```
[Базовый стиль] + [Текстовый якорь персонажа] + [Действие в этой сцене] + [Фон и окружение] + [Освещение и камера] + [Параметры генерации]
```

### Пример промпта для генератора изображений (Midjourney/Flux):
> **Промпт:** `3D Pixar style. A 25-year-old Kazakh guy, sharp jawline, short messy black hair, round black-rimmed glasses, wearing a solid blue hoodie. He is sitting at a wooden office desk, looking shocked at a glowing smartphone in his hand. Stacks of documents, coffee cup on the desk. Cozy warm office background, soft volumetric lighting, close-up shot, vivid colors, octane render --ar 9:16 --cref CHAR_URL --cw 0`

---

## 🎥 Шаг 3: Анимация кадров (Image-to-Video)

Никогда не генерируйте видео по чистому тексту (Text-to-Video), если вам нужен стабильный персонаж. Всегда используйте режим **Image-to-Video**:

1. Загрузите сгенерированное на Шаге 2 изображение в качестве **первого кадра** (First Frame / Image Prompt) в Luma Dream Machine, Kling, Runway Gen-3 или Google Veo.
2. Напишите текстовый промпт, который описывает **только движение и камеру**, не перегружая его описанием персонажа.

### Шаблон промпта для анимации (Luma / Kling / Google Veo):
> **Промпт:** `Pixar style animation. The young man gasps and opens his eyes wide in shock as he looks at his phone. The screen of the phone glows, reflecting light on his face. The camera slowly zooms in. Smooth character movements, high-quality 3D render, 5 seconds.`

---

## 🗣 Шаг 4: Озвучка и Анимация губ (Lip Sync)

1. **Голос (ElevenLabs):** Запишите свой голос или клонируйте его в ElevenLabs, чтобы персонаж говорил вашим голосом (это повышает доверие аудитории). Озвучьте реплики персонажа.
2. **Анимация губ (Lip Sync):** Используйте сервисы **SyncLabs** или **SadTalker** (а также HeyGen / LivePortrait), загрузив туда видео из Шага 3 и аудиофайл из ElevenLabs. Нейросеть идеально синхронизирует движение губ персонажа со звуком голоса.
3. **Монтаж (CapCut / Premiere Pro):** Соберите сцены вместе, наложите фоновую музыку, добавьте субтитры (с помощью встроенных авто-субтитров CapCut с красивым шрифтом и анимацией слов) и звуковые эффекты (SFX).
