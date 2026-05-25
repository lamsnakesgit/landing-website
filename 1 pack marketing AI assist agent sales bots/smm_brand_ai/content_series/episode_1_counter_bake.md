# Серия 1. «Счётчик Баке» — production-ready storyboard

**Формат:** вертикальное видео 9:16  
**Длина:** 28–35 секунд  
**Цель серии:** зацепить через кризис, аренду СТО, угрозу потери гаража и первый запуск AI-коллектора.  
**Функция в общей стратегии:** вирусный скетч + демонстрация пользы AI-автоматизации + клиффхэнгер на серию 2.  
**Стек:** Flux / NanoBanana для кадров, Google Veo для Image-to-Video, MiniMax / ElevenLabs для озвучки, FFmpeg / CapCut для финального монтажа.

---

## 0. Логлайн

Аха держит маленькое СТО в аренду и тонет в долгах. Баке приезжает за деньгами и ставит его на счётчик: до утра нужен 1 миллион тенге. Аха в панике бежит к Максу, а Макс вместо обычного займа запускает AI-коллектора, который начинает трясти деньги с должников автосервиса. Деньги приходят, но Баке внезапно поднимает ставку.

---

## 1. Почему ролик должен цеплять

### Хук

У зрителя за 2 секунды должна быть понятна ставка:

> «Если до утра не собрать миллион — СТО забирает Баке».

### Удержание

Каждые 4–6 секунд появляется новый стимул:

1. Баке приезжает.
2. Долг и дедлайн.
3. Аха в панике.
4. Макс спокойно запускает AI-коллектора.
5. Деньги начинают падать.
6. Баке повышает ставку.

### Коммерческий мост

Ролик не просто про Баке. Он продаёт идею:

> AI может возвращать деньги, дожимать клиентов, напоминать должникам и автоматизировать продажи.

CTA в конце:

> «Хочешь AI-коллектора для своего бизнеса — напиши “ДОЛГИ”».

---

## 2. Главные персонажи

### Аха

- молодой казахский парень, 24–28 лет;
- владелец маленького СТО;
- серый худи, рабочие штаны, кроссовки;
- добрый, нервный, немного наивный;
- лицо выразительное: паника, пот, большие глаза;
- архетип: «предприниматель в кассовом разрыве».

### Макс

- спокойный AI-разработчик, 25–30 лет;
- чёрный худи, ноутбук, энергетик;
- говорит мало, но уверенно;
- архетип: «человек, который автоматизирует хаос».

### Баке

- крупный строгий мужчина 40–50 лет;
- чёрная кожаная куртка, тёмные брюки;
- дорогие часы, суровое лицо;
- выглядит как жёсткий арендодатель/коллектор района, но без прямого насилия;
- архетип: «давление, дедлайн, деньги».

### AI-коллектор

- не человек, а визуальный цифровой персонаж;
- маленький голографический бот в кожаной куртке;
- говорит низким комичным голосом;
- делает не криминал, а автоматический обзвон должников и напоминания по оплате.

---

## 3. Ритм монтажа

| Время | Бит | Задача |
|---|---|---|
| 0:00–0:02 | Мгновенный хук | показать кризис |
| 0:02–0:07 | Баке ставит дедлайн | ставка и конфликт |
| 0:07–0:11 | Паника Ахи | эмоция и юмор |
| 0:11–0:17 | Макс запускает AI | решение |
| 0:17–0:24 | AI-коллектор работает | визуальный payoff |
| 0:24–0:30 | Деньги приходят | удовлетворение |
| 0:30–0:35 | Баке повышает ставку | клиффхэнгер |

---

## 4. Финальный сценарий с репликами

### Сцена 1 — «До утра миллион»  
**Тайминг:** 0:00–0:07

**Картинка:**  
Серый двор с гаражами. У вывески «СТО Аха» сидит Аха, рядом пустая касса, мятый блокнот, на экране телефона красное уведомление «Аренда просрочена». В кадр резко въезжает чёрный внедорожник. Из него выходит Баке.

**Текст на экране:**  
`ДО УТРА: 1 000 000 ₸`

**Реплики:**

- **Баке:** «Аха. До утра лимон за аренду СТО».
- **Аха:** «Баке, брат, кризис же… клиентов нет…»
- **Баке:** «Кризис у всех. Но гараж один».

**SFX:**

- визг тормозов;
- хлопок двери;
- низкий басовый удар;
- короткий звук таймера.

**Промпт для кадра Flux / NanoBanana:**

```text
Vertical 9:16, stylized 3D animated film look, expressive Pixar-like characters, post-soviet garage courtyard in Almaty, small auto repair shop sign "СТО Аха", young Kazakh man Axa in grey hoodie sitting on a tire, nervous and sweating, empty cash box and overdue rent paper near him, black SUV parked close, large stern Kazakh man Bake in black leather jacket standing in front of him, serious face, expensive watch, dramatic cloudy sky, cinematic lighting, high detail, emotional faces, safe comedic tension, no violence
```

**Промпт для Google Veo:**

```text
Vertical 9:16 animated scene. A black SUV stops sharply near a small garage. Bake, a large stern man in a black leather jacket, steps out and walks toward Axa. Axa sits on a tire, shrinking nervously. Camera starts wide, then pushes in toward Axa's scared face. Add dramatic but comedic tension, dust in the air, cinematic lighting, 5 seconds, no violence.
```

---

### Сцена 2 — «Паника и Макс»  
**Тайминг:** 0:07–0:12

**Картинка:**  
Аха врывается в маленькую комнату-офис. Макс сидит за ноутбуком спокойно, на экране n8n-схема, рядом энергетик. Аха машет руками, будто конец света.

**Текст на экране:**  
`КАССОВЫЙ РАЗРЫВ: УРОВЕНЬ БАКЕ`

**Реплики:**

- **Аха:** «Макс! Меня аренда сейчас съест!»
- **Макс:** «Сколько должны клиенты за старые ремонты?»
- **Аха:** «Много… но они не отвечают!»
- **Макс:** «Значит, ответят боту».

**SFX:**

- дверь резко открывается;
- быстрые шаги;
- спокойный глоток энергетика;
- механическая клавиатура.

**Промпт для кадра Flux / NanoBanana:**

```text
Vertical 9:16, stylized 3D animated film look, small messy programmer room with blue and pink neon lights, Max a calm smart Kazakh developer in black hoodie sitting at a glowing laptop with node automation diagrams on screen, energy drink cans on desk, Axa bursts into the room in panic waving hands, scared face, contrast between panic and calm, cinematic neon light, high detail, expressive faces
```

**Промпт для Google Veo:**

```text
Vertical 9:16 animated scene. Axa rushes into a neon-lit programmer room, panicking and waving his hands. Max stays calm, takes a sip from an energy drink, turns the laptop toward Axa. The screen shows glowing automation nodes and a big button "AI CALLER". Camera cuts between Axa's panic and Max's calm smile. 5 seconds.
```

---

### Сцена 3 — «Запуск AI-коллектора»  
**Тайминг:** 0:12–0:18

**Картинка:**  
Крупно ноутбук Макса. На экране схема: «Старые клиенты → AI-звонок → напоминание → оплата». Макс нажимает Enter. Над ноутбуком появляется маленький голографический AI-коллектор в кожанке, комично копирующий интонации Баке.

**Текст на экране:**  
`AI-КОЛЛЕКТОР ЗАПУЩЕН`

**Реплики:**

- **Макс:** «Сейчас он напомнит всем культурно… но убедительно».
- **AI-коллектор:** «Салам, Ерлан. За ремонт коробки долг висит. Оплатим красиво?»

**SFX:**

- запуск системы;
- цифровой «вжух»;
- короткий смешной басовый голос;
- всплывающие карточки клиентов.

**Промпт для кадра Flux / NanoBanana:**

```text
Vertical 9:16, stylized 3D animated film look, close-up of glowing laptop screen showing automation workflow: old customers, AI call, reminder, payment, green progress arrows. Max's finger presses Enter. Above the laptop appears a small holographic AI robot wearing a tiny black leather jacket, funny serious face, digital glow, Axa in background shocked, neon room, high detail, cinematic lighting
```

**Промпт для Google Veo:**

```text
Vertical 9:16 animated scene. Max presses Enter on the laptop. Automation nodes light up one by one. A small holographic AI collector appears above the laptop, wearing a tiny leather jacket and making serious gestures. Customer cards fly across the screen: "old repair debt", "call", "payment reminder". Axa's jaw drops. 6 seconds, dynamic glowing UI, comedic tone.
```

---

### Сцена 4 — «Деньги пошли»  
**Тайминг:** 0:18–0:26

**Картинка:**  
Крупный план телефона Ахи. Одно за другим появляются уведомления о переводах: +35 000 ₸, +80 000 ₸, +120 000 ₸. Аха сначала не верит, потом начинает улыбаться. Макс спокойно кивает.

**Текст на экране:**  
`+35 000 ₸`  
`+80 000 ₸`  
`+120 000 ₸`  
`ЕЩЁ 17 ОПЛАТ...`

**Реплики:**

- **Аха:** «Макс… они реально платят!»
- **Макс:** «Люди не любят долги. Просто им надо напомнить вовремя».

**SFX:**

- серия приятных уведомлений;
- ускоряющийся счётчик денег;
- лёгкий победный бит.

**Промпт для кадра Flux / NanoBanana:**

```text
Vertical 9:16, stylized 3D animated film look, close-up of smartphone in Axa's hand showing multiple incoming payment notifications in Kazakh tenge, green checkmarks, amounts like +35000 KZT, +80000 KZT, +120000 KZT, background shows Axa shocked but starting to smile, Max calm and confident, golden particles, high detail, cinematic glow, no real bank logos
```

**Промпт для Google Veo:**

```text
Vertical 9:16 animated close-up. Smartphone screen lights up with rapid incoming payment notifications, green checkmarks, money counter increasing. Golden particles burst softly around the phone. Axa's face changes from panic to disbelief to happiness. Max nods calmly in the background. 7 seconds, fast satisfying rhythm.
```

---

### Сцена 5 — «Баке передумал»  
**Тайминг:** 0:26–0:35

**Картинка:**  
Аха уже почти выдыхает. Вдруг телефон темнеет. Приходит новое сообщение от Баке: «Красиво работаешь. Теперь до утра два лимона». На лице Ахи снова ужас. Макс чуть улыбается, будто уже придумал следующий ход.

**Текст на экране:**  
`БАКЕ: "ТЕПЕРЬ 2 000 000 ₸"`  
`Продолжение: AI-коллектор против Баке`

**Реплики:**

- **Аха:** «Он… поднял счётчик».
- **Макс:** «Тогда завтра подключим должников Баке».
- **AI-коллектор:** «О, это уже интересно».

**SFX:**

- резкий стоп музыки;
- тревожный бас;
- вибрация телефона;
- короткий glitch;
- финальный драматичный удар.

**Промпт для кадра Flux / NanoBanana:**

```text
Vertical 9:16, stylized 3D animated film look, dramatic close-up of smartphone screen with a red message from "Bake": "Теперь 2 000 000 ₸". Axa in the background looks terrified again, eyes wide, Max stands beside him with a small confident smile, tiny holographic AI collector looks excited, neon lighting, cinematic contrast, cliffhanger mood, high detail
```

**Промпт для Google Veo:**

```text
Vertical 9:16 animated scene. The phone screen suddenly darkens, then a red message from Bake appears: "Теперь 2 000 000 ₸". The music stops. Axa freezes in terror. Max slowly smiles and looks at the holographic AI collector. The tiny AI collector cracks its neck digitally and glows brighter. Camera zooms in on the red message, then cuts to black. 6 seconds, cliffhanger.
```

---

## 5. Финальная озвучка одним блоком

```text
[SFX: резкий визг тормозов, хлопок двери, низкий бас]

Баке: Аха. До утра лимон за аренду СТО.
Аха: Баке, брат, кризис же… клиентов нет…
Баке: Кризис у всех. Но гараж один.

[SFX: быстрые шаги, дверь открывается]

Аха: Макс! Меня аренда сейчас съест!
Макс: Сколько должны клиенты за старые ремонты?
Аха: Много… но они не отвечают!
Макс: Значит, ответят боту.

[SFX: клавиатура, запуск системы]

Макс: Сейчас он напомнит всем культурно… но убедительно.
AI-коллектор: Салам, Ерлан. За ремонт коробки долг висит. Оплатим красиво?

[SFX: быстрые уведомления о переводах]

Аха: Макс… они реально платят!
Макс: Люди не любят долги. Просто им надо напомнить вовремя.

[SFX: резкий стоп музыки, вибрация телефона]

Аха: Он… поднял счётчик.
Макс: Тогда завтра подключим должников Баке.
AI-коллектор: О, это уже интересно.
```

---

## 6. Тексты на экране

1. `ДО УТРА: 1 000 000 ₸`
2. `КАССОВЫЙ РАЗРЫВ: УРОВЕНЬ БАКЕ`
3. `AI-КОЛЛЕКТОР ЗАПУЩЕН`
4. `+35 000 ₸`
5. `+80 000 ₸`
6. `+120 000 ₸`
7. `ЕЩЁ 17 ОПЛАТ...`
8. `БАКЕ: "ТЕПЕРЬ 2 000 000 ₸"`
9. `Продолжение: AI-коллектор против Баке`
10. `Хочешь такого бота для бизнеса? Напиши “ДОЛГИ”`

---

## 7. Монтажные указания

### Темп

- первые 2 секунды — максимально быстрый кризис;
- сцена Баке — тяжёлый, низкий звук;
- сцена Макса — резкий контраст: спокойствие и неон;
- сцена денег — ускорение, зелёные уведомления, удовлетворение;
- финал — резкая остановка и клиффхэнгер.

### Переходы

- Сцена 1 → 2: whip pan или резкий blur от лица Ахи.
- Сцена 2 → 3: zoom в экран ноутбука.
- Сцена 3 → 4: цифровой swipe из UI в телефон.
- Сцена 4 → 5: уведомления резко гаснут, экран краснеет.
- Финал: cut to black + текст продолжения.

### Музыка

- начало: мрачный синтвейв / trap bass;
- середина: быстрый tech beat;
- деньги: короткий победный подъём;
- финал: bass drop + тишина.

---

## 8. Проверка перед генерацией

- [x] Есть сильная ставка в первые 2 секунды.
- [x] Понятно, почему Аха в кризисе.
- [x] Баке требует деньги за аренду СТО.
- [x] Есть AI-решение, а не просто шутка.
- [x] AI-коллектор встроен в сюжет.
- [x] Есть визуальный прогресс денег.
- [x] Есть клиффхэнгер на серию 2.
- [x] Есть коммерческий мост к продукту/услуге.
- [x] Есть промпты для кадров.
- [x] Есть промпты для анимации.
- [x] Есть озвучка и SFX.
- [x] Есть тексты на экране.
- [x] Есть монтажные указания.

---

## 9. Следующий шаг

Сгенерировать 5 базовых кадров:

1. Баке у гаража требует аренду.
2. Аха в панике у Макса.
3. Макс запускает AI-коллектора.
4. Телефон с входящими оплатами.
5. Сообщение Баке про 2 миллиона.

После этого прогнать каждый кадр через Image-to-Video и собрать черновой монтаж на 28–35 секунд.