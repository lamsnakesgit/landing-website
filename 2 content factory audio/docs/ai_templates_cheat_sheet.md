# 🎨 Шаблоны контента: "Media Factory" (Ready-to-use)

Используй эти промпты и структуру для своих веток в n8n. Это "хуки", которые помогут продавать бот разным аудиториям.

---

## 📸 1. Шаблоны "ИИ-Фотосессия" (Portrait & Identity)
**Логика**: Юзер присылает селфи -> мы используем `Imagen 4` с параметром `reference_image`.

| Стиль | Промпт для Imagen | Описание для юзера |
| :--- | :--- | :--- |
| **Old Money / Royal** | "Cinetic portrait of [USER_REF] as a wealthy billionaire, wearing a luxury ivory linen suit on a yacht in Monaco. Soft sunlight, film grain, 8k." | "Стань героем списка Forbes за 5 секунд." |
| **Cyberpunk 2077** | "Hyper-realistic portrait of [USER_REF] in a neon-lit futuristic city, wearing robotic armor with glowy LED lights. Cyberpunk style, high contrast." | "Твое фото прямиком из будущего Найт-Сити." |
| **LinkedIn Professional** | "Professional headshot of [USER_REF] in a business suit, light grey studio background, high quality lighting, corporate style, 8k." | "Идеальное фото для резюме и рабочих соцсетей." |
| **Anime Style (Arcane)** | "Stylized Arcane-style digital painting of [USER_REF], vibrant colors, expressive hand-drawn textures, cinematic shading." | "Превратись в персонажа легендарного мультсериала." |

---

## 🖼️ 2. Шаблоны "Генерация Артов" (Creative Art)
**Логика**: Просто чистый полет фантазии для сторис и блогов.

| Тема | Промпт для Imagen |
| :--- | :--- |
| **3D Изометрия** | "3D isometric render of a cozy high-tech home office on a small floating island, soft pastel colors, Octane render, cute aesthetic." |
| **Стиль "Apple"** | "Minimalist close-up shot of a glass tech device, futuristic design, white studio background, hard shadows, ultra-modern." |
| **Масло/Живопись** | "Vibrant oil painting of a busy London street in the rain at night, thick brushstrokes, impressionism, glowing city lights." |

---

## 📝 3. Шаблон "Статья + Картинка" (Content Maker)
**Логика**: Gemini пишет пост -> Imagen делает обложку.

**Шаблон для Gemini (System Prompt):**
> "Ты — топовый копирайтер. Напиши пост для Telegram на тему [Твоя тема]. 
> Структура: 
> 1. 🔥 Хайповый заголовок. 
> 2. 🤔 Проблема/Боль. 
> 3. ✅ Решение (3-5 пунктов). 
> 4. 📢 Призыв к действию (CTA).
> В конце добавь промпт на английском для генерации идеальной обложки к этому посту."

**Пример вывода:**
*   **Пост**: "Как не выгореть в 2026?..."
*   **Промпт для обложки**: "A tired manager sitting at a desk made of paper stacks, suddenly glowing with green digital energy, surreal conceptual art, 4k."

---

## 🔥 Лайфхак для бизнеса:
Продавай "Пакеты": 
- **Пакет "Блогер"**: 10 сгенерированных статей + 10 уникальных обложек к ним. 
- **Пакет "Аватар"**: 5 фотосессий в разных стилях. 

* phoenix-crystal.io / t.me/nnsvt *
