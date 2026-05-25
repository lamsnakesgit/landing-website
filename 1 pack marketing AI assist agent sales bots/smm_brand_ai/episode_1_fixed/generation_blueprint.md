# Episode 1 Fixed — план догенерации персонажей, кадров и Veo 3.1 Lite

## Короткий статус

В папке `smm_brand_ai/episode_1_fixed/` уже есть:

- 3 character prompt файла:
  - `axa_character_prompt.md`
  - `max_character_prompt.md`
  - `bake_character_prompt.md`
- 5 scene prompt файлов:
  - `scene_01_prompt.md`
  - `scene_02_prompt.md`
  - `scene_03_prompt.md`
  - `scene_04_prompt.md`
  - `scene_05_prompt.md`
- 3 готовых варианта первого кадра:
  - `scene_01_v1.png`
  - `scene_01_v2.png`
  - `scene_01_v3.png`

Чего не хватает для нормальной генерации:

- [ ] 9 ракурсов Ахи.
- [ ] 9 ракурсов Макса.
- [ ] 9 ракурсов Баке.
- [ ] 9 ракурсов AI-коллектора.
- [ ] Start frame и end frame для каждой из 5 сцен.
- [ ] Финальные image prompts под каждый start/end frame.
- [ ] Veo 3.1 Lite prompts под каждую сцену с указанием start/end frames.
- [ ] Единый naming convention, чтобы не запутаться в генерациях.

---

## 1. Единый visual bible

### Общий стиль

Использовать один и тот же стиль во всех кадрах:

```text
Vertical 9:16, stylized 3D animated film look, expressive Pixar-like characters, high detail, cinematic lighting, soft realistic materials, emotional faces, comedic dramatic tension, Almaty post-soviet urban details, no violence, no blood, no real brand logos
```

### Negative prompt

```text
inconsistent face, different outfit, extra fingers, deformed hands, blurry face, distorted eyes, wrong age, different hairstyle, realistic live-action, horror, violence, blood, weapons, real bank logos, readable brand logos, watermark, text artifacts
```

### Цветовая логика

- Сцена Баке: серый двор, холодный свет, низкий контраст, тревога.
- Сцена Макса: синий/розовый неон, tech vibe, спокойствие.
- AI-коллектор: зелёно-голубой digital glow.
- Деньги: зелёные уведомления + золотые частицы.
- Клиффхэнгер: красный экран + тёмный контраст.

---

## 2. Naming convention

### Character reference frames

```text
characters/axa/axa_angle_01_front.png
characters/axa/axa_angle_02_3q_left.png
characters/axa/axa_angle_03_left_profile.png
characters/axa/axa_angle_04_back_3q_left.png
characters/axa/axa_angle_05_back.png
characters/axa/axa_angle_06_back_3q_right.png
characters/axa/axa_angle_07_right_profile.png
characters/axa/axa_angle_08_3q_right.png
characters/axa/axa_angle_09_emotion_sheet.png

characters/max/max_angle_01_front.png
...
characters/bake/bake_angle_01_front.png
...
characters/ai_collector/ai_collector_angle_01_front.png
...
```

### Scene frames

```text
frames/scene_01_start.png
frames/scene_01_end.png
frames/scene_02_start.png
frames/scene_02_end.png
frames/scene_03_start.png
frames/scene_03_end.png
frames/scene_04_start.png
frames/scene_04_end.png
frames/scene_05_start.png
frames/scene_05_end.png
```

### Video outputs

```text
video/scene_01_veo_lite.mp4
video/scene_02_veo_lite.mp4
video/scene_03_veo_lite.mp4
video/scene_04_veo_lite.mp4
video/scene_05_veo_lite.mp4
video/episode_01_counter_bake_rough_cut.mp4
```

---

## 3. 9 ракурсов персонажей

### 3.1 Axa — 9 ракурсов

Базовый identity prompt:

```text
Consistent character reference sheet for Axa, young Kazakh male, 24-28 years old, slim build, slightly messy black hair, warm brown eyes, light tan skin, expressive nervous face, grey oversized hoodie, dark work pants, worn sneakers, kind naive young auto-service owner, stylized 3D animated film look, Pixar-like expressive face, high detail, clean studio background, same outfit in every view, same face in every view
```

#### Axa angle 01 — front

```text
{Axa identity prompt}, full body front view, neutral standing pose, arms relaxed, looking slightly worried, clean light grey background, vertical 9:16
```

#### Axa angle 02 — 3/4 left

```text
{Axa identity prompt}, full body 3/4 left view, nervous posture, shoulders slightly raised, same grey hoodie and dark work pants, clean light grey background, vertical 9:16
```

#### Axa angle 03 — left profile

```text
{Axa identity prompt}, full body left side profile view, slim silhouette, messy black hair clearly visible, anxious expression, clean light grey background, vertical 9:16
```

#### Axa angle 04 — back 3/4 left

```text
{Axa identity prompt}, full body back 3/4 left view, hood shape visible, worn sneakers, same outfit, clean light grey background, vertical 9:16
```

#### Axa angle 05 — back

```text
{Axa identity prompt}, full body back view, grey oversized hoodie from behind, dark work pants, clean light grey background, vertical 9:16
```

#### Axa angle 06 — back 3/4 right

```text
{Axa identity prompt}, full body back 3/4 right view, same body proportions, same hairstyle, clean light grey background, vertical 9:16
```

#### Axa angle 07 — right profile

```text
{Axa identity prompt}, full body right side profile view, worried face profile, same outfit, clean light grey background, vertical 9:16
```

#### Axa angle 08 — 3/4 right

```text
{Axa identity prompt}, full body 3/4 right view, nervous but kind expression, hands slightly open, clean light grey background, vertical 9:16
```

#### Axa angle 09 — emotion sheet

```text
{Axa identity prompt}, character emotion sheet, 6 head expressions in one vertical sheet: terrified, panicking, confused, shocked, relieved, nervous smile, same face and hair, clean light grey background, vertical 9:16
```

---

### 3.2 Max — 9 ракурсов

Базовый identity prompt:

```text
Consistent character reference sheet for Max, smart Kazakh male, 25-30 years old, average build, short neat black hair, calm focused face, light tan skin, black hoodie, dark jeans, sneakers, calm AI developer, confident, relaxed under pressure, stylized 3D animated film look, Pixar-like expressive face, high detail, clean studio background, same outfit in every view, same face in every view
```

#### Max angle 01 — front

```text
{Max identity prompt}, full body front view, neutral calm standing pose, slight confident smile, clean light grey background, vertical 9:16
```

#### Max angle 02 — 3/4 left

```text
{Max identity prompt}, full body 3/4 left view, calm posture, hands in hoodie pocket, clean light grey background, vertical 9:16
```

#### Max angle 03 — left profile

```text
{Max identity prompt}, full body left side profile view, focused expression, short neat hair visible, clean light grey background, vertical 9:16
```

#### Max angle 04 — back 3/4 left

```text
{Max identity prompt}, full body back 3/4 left view, black hoodie silhouette, dark jeans, clean light grey background, vertical 9:16
```

#### Max angle 05 — back

```text
{Max identity prompt}, full body back view, black hoodie from behind, relaxed posture, clean light grey background, vertical 9:16
```

#### Max angle 06 — back 3/4 right

```text
{Max identity prompt}, full body back 3/4 right view, same body proportions, clean light grey background, vertical 9:16
```

#### Max angle 07 — right profile

```text
{Max identity prompt}, full body right side profile view, calm focused expression, clean light grey background, vertical 9:16
```

#### Max angle 08 — 3/4 right

```text
{Max identity prompt}, full body 3/4 right view, confident relaxed pose, one hand holding a small energy drink can, clean light grey background, vertical 9:16
```

#### Max angle 09 — emotion sheet

```text
{Max identity prompt}, character emotion sheet, 6 head expressions in one vertical sheet: calm, confident smile, focused, amused, serious, "I have a plan" smirk, same face and hair, clean light grey background, vertical 9:16
```

---

### 3.3 Bake — 9 ракурсов

Базовый identity prompt:

```text
Consistent character reference sheet for Bake, large stern Kazakh male, 42-50 years old, heavy muscular build, short black hair, thick eyebrows, square jaw, serious intimidating face but comedic, light tan skin, black leather jacket, dark trousers, black shoes, gold watch, strict local landlord and debt collector type, pressure and deadline, no violence, stylized 3D animated film look, Pixar-like expressive face, high detail, clean studio background, same outfit in every view, same face in every view
```

#### Bake angle 01 — front

```text
{Bake identity prompt}, full body front view, stern standing pose, arms crossed, gold watch visible, clean light grey background, vertical 9:16
```

#### Bake angle 02 — 3/4 left

```text
{Bake identity prompt}, full body 3/4 left view, pointing down with one finger, serious expression, clean light grey background, vertical 9:16
```

#### Bake angle 03 — left profile

```text
{Bake identity prompt}, full body left side profile view, square jaw profile, leather jacket silhouette, clean light grey background, vertical 9:16
```

#### Bake angle 04 — back 3/4 left

```text
{Bake identity prompt}, full body back 3/4 left view, broad shoulders, black leather jacket back, clean light grey background, vertical 9:16
```

#### Bake angle 05 — back

```text
{Bake identity prompt}, full body back view, large silhouette, black leather jacket, clean light grey background, vertical 9:16
```

#### Bake angle 06 — back 3/4 right

```text
{Bake identity prompt}, full body back 3/4 right view, broad shoulders, same proportions, clean light grey background, vertical 9:16
```

#### Bake angle 07 — right profile

```text
{Bake identity prompt}, full body right side profile view, stern face profile, thick eyebrows, clean light grey background, vertical 9:16
```

#### Bake angle 08 — 3/4 right

```text
{Bake identity prompt}, full body 3/4 right view, one hand adjusting gold watch, serious comedic pressure, clean light grey background, vertical 9:16
```

#### Bake angle 09 — emotion sheet

```text
{Bake identity prompt}, character emotion sheet, 6 head expressions in one vertical sheet: stern, suspicious, angry but comedic, surprised, impressed, wide proud smile, same face and hair, clean light grey background, vertical 9:16
```

---

### 3.4 AI-коллектор — 9 ракурсов

Базовый identity prompt:

```text
Consistent character reference sheet for AI Collector, tiny holographic digital robot, small humanoid assistant, wearing a miniature black leather jacket inspired by Bake, glowing cyan and green edges, funny serious face, expressive digital eyes, confident collector attitude, comedic not scary, stylized 3D animated film look, high detail, semi-transparent hologram material, clean dark background, same design in every view
```

#### AI Collector angle 01 — front

```text
{AI Collector identity prompt}, full body front view, tiny holographic robot standing confidently, hands on hips, vertical 9:16
```

#### AI Collector angle 02 — 3/4 left

```text
{AI Collector identity prompt}, full body 3/4 left view, pointing like a tiny serious collector, vertical 9:16
```

#### AI Collector angle 03 — left profile

```text
{AI Collector identity prompt}, full body left side profile view, glowing cyan outline, tiny leather jacket, vertical 9:16
```

#### AI Collector angle 04 — back 3/4 left

```text
{AI Collector identity prompt}, full body back 3/4 left view, semi-transparent hologram glow, vertical 9:16
```

#### AI Collector angle 05 — back

```text
{AI Collector identity prompt}, full body back view, tiny black leather jacket from behind, digital glow, vertical 9:16
```

#### AI Collector angle 06 — back 3/4 right

```text
{AI Collector identity prompt}, full body back 3/4 right view, holographic particles, vertical 9:16
```

#### AI Collector angle 07 — right profile

```text
{AI Collector identity prompt}, full body right side profile view, serious funny face profile, vertical 9:16
```

#### AI Collector angle 08 — 3/4 right

```text
{AI Collector identity prompt}, full body 3/4 right view, cracking tiny digital knuckles in a comedic way, vertical 9:16
```

#### AI Collector angle 09 — emotion sheet

```text
{AI Collector identity prompt}, character emotion sheet, 6 digital face expressions in one vertical sheet: serious, excited, suspicious, smug, calculating, happy, same robot design, vertical 9:16
```

---

## 4. Start / end frames по сценам

### Scene 01 — Баке ставит дедлайн

#### scene_01_start.png

```text
Vertical 9:16, stylized 3D animated film look, post-soviet garage courtyard in Almaty, small auto repair shop sign "СТО Аха", Axa sitting on a tire near an empty cash box and overdue rent paper, Axa nervous and sweating, black SUV just arrived in the background, Bake is stepping out of the SUV, dramatic cloudy sky, cold grey light, cinematic composition, no violence, no real brand logos
```

#### scene_01_end.png

```text
Vertical 9:16, stylized 3D animated film look, close dramatic composition near the garage, Bake stands in front of Axa pointing at the overdue rent paper, Axa shrinks nervously on the tire, text space at top for "ДО УТРА: 1 000 000 ₸", strong comedic pressure, cinematic lighting, no violence, same Axa and Bake as reference
```

#### Veo 3.1 Lite prompt

```text
Use scene_01_start.png as the start frame and scene_01_end.png as the end frame. Vertical 9:16, 5 seconds. A black SUV stops near the garage, Bake steps out and approaches Axa. Axa sits on the tire and becomes visibly nervous. Camera starts wide, then slowly pushes in toward Axa and Bake. Keep the same character faces, same outfits, same garage location. Dramatic but comedic tension, no violence, no blood. Add dust and a low bass hit at the end.
```

---

### Scene 02 — Аха прибегает к Максу

#### scene_02_start.png

```text
Vertical 9:16, stylized 3D animated film look, small neon-lit programmer room, Max calmly sitting at laptop with blue and pink neon lighting, energy drink can on desk, laptop screen shows simple automation nodes, the door is closed, calm before chaos, high detail, same Max as reference
```

#### scene_02_end.png

```text
Vertical 9:16, stylized 3D animated film look, same programmer room, Axa bursts through the door in panic waving his hands, Max remains calm at the laptop and turns toward him, strong contrast between panic and calm, blue and pink neon lighting, same Axa and Max as reference
```

#### Veo 3.1 Lite prompt

```text
Use scene_02_start.png as the start frame and scene_02_end.png as the end frame. Vertical 9:16, 5 seconds. Start with Max calmly working at the laptop in a neon-lit room. Axa suddenly rushes in, panicking and waving his hands. Max stays relaxed, takes a sip from an energy drink, and turns the laptop toward Axa. Keep the same character faces and outfits. Comedic contrast: Axa is chaos, Max is calm.
```

---

### Scene 03 — Запуск AI-коллектора

#### scene_03_start.png

```text
Vertical 9:16, stylized 3D animated film look, close-up of Max's laptop screen in neon room, automation workflow visible: old customers → AI call → reminder → payment, Max's finger above Enter key, Axa in background shocked, no hologram yet, same characters as reference
```

#### scene_03_end.png

```text
Vertical 9:16, stylized 3D animated film look, Max presses Enter, automation nodes glowing green and blue, small holographic AI Collector appears above the laptop wearing a tiny black leather jacket, Axa shocked in the background, digital particles, high detail, same Max, Axa, and AI Collector as reference
```

#### Veo 3.1 Lite prompt

```text
Use scene_03_start.png as the start frame and scene_03_end.png as the end frame. Vertical 9:16, 6 seconds. Max presses Enter. Automation nodes light up one by one. A small holographic AI Collector appears above the laptop, wearing a tiny leather jacket and making serious comedic gestures. Customer cards fly across the screen: "old repair debt", "call", "payment reminder". Axa's jaw drops. Dynamic glowing UI, comedic tone, keep all characters consistent.
```

---

### Scene 04 — Деньги пошли

#### scene_04_start.png

```text
Vertical 9:16, stylized 3D animated film look, close-up of smartphone in Axa's hand, screen just lights up with first incoming payment notification +35 000 ₸, Axa still looks shocked and unsure, Max calm in background, green glow from phone, no real bank logos, same Axa and Max as reference
```

#### scene_04_end.png

```text
Vertical 9:16, stylized 3D animated film look, same smartphone now filled with many incoming payment notifications in Kazakh tenge: +35 000 ₸, +80 000 ₸, +120 000 ₸, "ЕЩЁ 17 ОПЛАТ...", Axa starts smiling in disbelief, Max nods calmly, golden particles, no real bank logos, same characters as reference
```

#### Veo 3.1 Lite prompt

```text
Use scene_04_start.png as the start frame and scene_04_end.png as the end frame. Vertical 9:16, 7 seconds. The smartphone screen rapidly fills with green payment notifications and a rising money counter. Golden particles appear around the phone. Axa's expression changes from panic to disbelief to happy relief. Max nods calmly in the background. Fast satisfying rhythm, no real bank logos, keep text clean and minimal.
```

---

### Scene 05 — Баке повышает ставку

#### scene_05_start.png

```text
Vertical 9:16, stylized 3D animated film look, Axa holding smartphone and almost smiling with relief, Max beside him calm, tiny holographic AI Collector floating near laptop, green payment glow still visible, neon room, same characters as reference
```

#### scene_05_end.png

```text
Vertical 9:16, stylized 3D animated film look, dramatic close-up of smartphone screen with red message from "Bake": "Теперь 2 000 000 ₸", Axa in background terrified again, Max with a small confident smile, tiny holographic AI Collector excited and glowing brighter, dark red cliffhanger mood, same characters as reference, no real bank logos
```

#### Veo 3.1 Lite prompt

```text
Use scene_05_start.png as the start frame and scene_05_end.png as the end frame. Vertical 9:16, 6 seconds. The phone screen suddenly darkens, then a red message from Bake appears: "Теперь 2 000 000 ₸". Music stops. Axa freezes in terror. Max slowly smiles and looks at the holographic AI Collector. The tiny AI Collector glows brighter, excited for the next challenge. Camera zooms into the red message, then cuts to black. Cliffhanger, keep character consistency.
```

---

## 5. Порядок генерации

### Шаг 1 — персонажные refs

Сначала генерировать не сцены, а character reference:

1. Axa 9 angles.
2. Max 9 angles.
3. Bake 9 angles.
4. AI Collector 9 angles.

После генерации выбрать лучший consistent set и использовать его как reference для сцен.

### Шаг 2 — scene start/end frames

Генерировать в таком порядке:

1. `scene_01_start.png`
2. `scene_01_end.png`
3. `scene_02_start.png`
4. `scene_02_end.png`
5. `scene_03_start.png`
6. `scene_03_end.png`
7. `scene_04_start.png`
8. `scene_04_end.png`
9. `scene_05_start.png`
10. `scene_05_end.png`

### Шаг 3 — Veo 3.1 Lite

Отправлять каждую сцену отдельно:

1. Start frame.
2. End frame.
3. Veo prompt.
4. Duration.
5. Vertical 9:16.
6. Character consistency priority.

### Шаг 4 — rough cut

Склеить:

1. `scene_01_veo_lite.mp4`
2. `scene_02_veo_lite.mp4`
3. `scene_03_veo_lite.mp4`
4. `scene_04_veo_lite.mp4`
5. `scene_05_veo_lite.mp4`

Потом добавить:

- voiceover;
- SFX;
- subtitles;
- screen text;
- final CTA.

---

## 6. Проверка готовности

Перед отправкой в генератор проверить:

- [ ] У каждого персонажа есть 9 reference views.
- [ ] Все персонажи в сценах совпадают с refs.
- [ ] Есть start/end frame для каждой сцены.
- [ ] В каждом Veo prompt указан start frame и end frame.
- [ ] В каждом Veo prompt указан vertical 9:16.
- [ ] В каждом Veo prompt указан duration.
- [ ] Нет реальных логотипов банков.
- [ ] Нет насилия, крови, оружия.
- [ ] Ставка понятна в первые 2 секунды.
- [ ] Финальный клиффхэнгер ведёт в серию 2.
- [ ] CTA ведёт в коммерческий мост: `ДОЛГИ`.

---

## 7. Минимальный набор файлов, который нужно догенерировать

```text
characters/axa/axa_angle_01_front.png
characters/axa/axa_angle_02_3q_left.png
characters/axa/axa_angle_03_left_profile.png
characters/axa/axa_angle_04_back_3q_left.png
characters/axa/axa_angle_05_back.png
characters/axa/axa_angle_06_back_3q_right.png
characters/axa/axa_angle_07_right_profile.png
characters/axa/axa_angle_08_3q_right.png
characters/axa/axa_angle_09_emotion_sheet.png

characters/max/max_angle_01_front.png
characters/max/max_angle_02_3q_left.png
characters/max/max_angle_03_left_profile.png
characters/max/max_angle_04_back_3q_left.png
characters/max/max_angle_05_back.png
characters/max/max_angle_06_back_3q_right.png
characters/max/max_angle_07_right_profile.png
characters/max/max_angle_08_3q_right.png
characters/max/max_angle_09_emotion_sheet.png

characters/bake/bake_angle_01_front.png
characters/bake/bake_angle_02_3q_left.png
characters/bake/bake_angle_03_left_profile.png
characters/bake/bake_angle_04_back_3q_left.png
characters/bake/bake_angle_05_back.png
characters/bake/bake_angle_06_back_3q_right.png
characters/bake/bake_angle_07_right_profile.png
characters/bake/bake_angle_08_3q_right.png
characters/bake/bake_angle_09_emotion_sheet.png

characters/ai_collector/ai_collector_angle_01_front.png
characters/ai_collector/ai_collector_angle_02_3q_left.png
characters/ai_collector/ai_collector_angle_03_left_profile.png
characters/ai_collector/ai_collector_angle_04_back_3q_left.png
characters/ai_collector/ai_collector_angle_05_back.png
characters/ai_collector/ai_collector_angle_06_back_3q_right.png
characters/ai_collector/ai_collector_angle_07_right_profile.png
characters/ai_collector/ai_collector_angle_08_3q_right.png
characters/ai_collector/ai_collector_angle_09_emotion_sheet.png

frames/scene_01_start.png
frames/scene_01_end.png
frames/scene_02_start.png
frames/scene_02_end.png
frames/scene_03_start.png
frames/scene_03_end.png
frames/scene_04_start.png
frames/scene_04_end.png
frames/scene_05_start.png
frames/scene_05_end.png