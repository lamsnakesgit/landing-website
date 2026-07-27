# 🎬 Gemini Omni — Гайд по видеогенерации с аудио

> Источники: r/VEO3, r/GeminiAI, replicate.com, piapi.ai, ltx.io

---

## ⚡ Ключевое отличие Omni от Veo 3.1

| Параметр | Gemini Omni | Veo 3.1 |
|---|---|---|
| Аудио/диалог | ✅ Нативно, мощно | ✅ Есть, но слабее |
| Следование референсам | ⚠️ Слабое (вдохновляется) | ✅ Сильнее |
| Референсов принимает | **до 14 файлов** | до 3 фото |
| Видео-референс | ✅ Да | ❌ Нет |
| Лучше использовать | Диалог + атмосфера | Персонаж + стиль |

---

## 🎯 Лайфхак с видео-референсом (ГЛАВНОЕ)

> *"Omni is insanely good if you upload 8-12 seconds of reference video"* — r/VEO3

**Как это работает:**
- Omni плохо держит персонажа по фотографиям
- НО если загрузить **видео 8-60 секунд** с персонажем — он понимает его в разы лучше
- Принимает до **14 файлов** — можно микс из видео + фото

**Практика для нашего проекта:**
1. Возьми любое видео с Ахой (из телефона, 30-60 сек)
2. Загрузи его в Omni как референс
3. + добавь 3-5 наших сгенеренных фото крупного плана
4. Итого = 6-8 референс-файлов → Omni "запомнит" персонажа

---

## 📝 Структура правильного промпта для Omni

```
[ВИДЕО]
Vertical 9:16. [Тип кадра]. [Описание сцены и действия].
[Персонаж] says in Russian: "[Диалог в кавычках]".
[Звуковая атмосфера]. Photorealistic. NO SUBTITLES.

[АУДИО — пишется ВНУТРИ основного промпта, не отдельно]
Ambient sound: [описание фоновых звуков].
[Имя персонажа] says: "[Текст реплики]"
[Имя 2] replies calmly: "[Ответная реплика]"
```

---

## ✅ Правила написания диалога

1. **Всегда в кавычках:**  
   ✅ `He says: "Макс, выручай!"`  
   ❌ `He says Макс, выручай`

2. **Указывай тон голоса:**  
   `He says desperately in Russian: "..."`  
   `She replies calmly with a smirk: "..."`

3. **Звуки описывай словами прямо в тексте:**  
   `The sound of rapid footsteps echoes in the corridor.`  
   `A heavy metal door slams open with a loud bang.`

4. **Явно проси аудио в начале промпта:**  
   `Please generate this video with full audio, dialogue, and sound effects.`

5. **Запрет субтитров — обязательно:**  
   `NO TEXT OVERLAYS. NO SUBTITLES. (no subtitles) NO CAPTIONS.`  
   *(повторить 2-3 раза — работает лучше)*

---

## 🚫 Триггерные слова — что блочит Omni

| Запрещено | Замена |
|---|---|
| `violently` | убрать или `quickly` |
| `bursts through` | `pushes through`, `runs through` |
| `panic`, `terrified` | `distressed`, `overwhelmed` |
| `debt`, `loan`, название банков | `financial problem`, `money issue` |
| `grabbing head in panic` | `places hand on forehead` |
| Мат в диалоге (`пиздец`) | `нам хана`, `нам конец` |

---

## 🎬 Готовый промпт-шаблон для Сцены 3

```
Please generate this video with full audio, dialogue, and sound effects.

Vertical 9:16. Continuous action shot. A young Kazakh man, 22 years old, 
clean-shaven with messy dark hair, wearing a grey zip-up hoodie over a 
white t-shirt, is leaning against a dark concrete wall looking completely 
dazed. The sound of his slow breathing fills the silence. He suddenly 
pushes off the wall and runs forward at full speed. The sound of his rapid 
footsteps echo loudly through the concrete hallway. He pushes through a 
heavy metal door — a loud bang fills the audio. He enters a dark room lit 
by glowing computer monitors and stops near a desk, panting. He says 
desperately in Russian: "Макс, выручай! Нам хана! Завтра лимон надо 
отдать, иначе выселяют с точки!" Another calm young man at the desk slowly 
turns and replies confidently in Russian: "Не суетись. Сейчас мой ИИ-бот 
всё порешает." Cinematic lighting. Photorealistic. NO TEXT OVERLAYS. 
NO SUBTITLES. NO CAPTIONS.
```

---

## 💡 Workflow для создания сцены

```
1. Собери референсы (до 14 файлов):
   - Видео с персонажем 30-60 сек (из телефона)
   - 5-6 сгенеренных фото крупного плана персонажа
   
2. Загрузи все в Omni одновременно

3. Добавь промпт по шаблону выше

4. Если заблочило — убери триггерные слова (см. таблицу)

5. Скачивай в 720p (НЕ 1080p — аудио теряется при апскейле!)

6. Монтируй сцены в CapCut/Premiere отдельно
```

---

*Обновлено: 2026-07-27*
