# Google AI Content Factory: 190€ Budget Strategy

This plan explains how to turn your 190€ Google Cloud credits into **300+ high-quality videos** using the most efficient AI models.

## 1. The Math (Cost Breakdown)

To maximize the budget, we use **Gemini 1.5 Flash** (fast/cheap) and **Imagen 3** (high quality).

| Service | Model | Cost per Video (approx.) | Videos for 190€ |
| :--- | :--- | :--- | :--- |
| **Scripting** | Gemini 1.5 Flash | €0.005 (5000 tokens) | 38,000 |
| **Images** | Imagen 3 (Fast) | €0.03 x 15 images = €0.45 | 422 |
| **Voiceover** | Google TTS (Studio) | €0.10 (per 1 min) | 1,900 |
| **Total** | | **~€0.55 per video** | **~345 Videos** |

---

## 2. The "Modular Scene" Workflow

Instead of generating one long video, we generate **Scenes**. This is faster and more reliable.

1.  **Step 1: Script & Scene Split (Gemini)**
    - Ask Gemini to write a script and immediately split it into 10-15 scenes.
    - For each scene, Gemini must provide:
        - `audio_text`: What the voice says.
        - `image_prompt`: A detailed prompt for Imagen 3.
2.  **Step 2: Batch Image Generation (Imagen 3)**
    - Send all 15 image prompts to the API at once.
3.  **Step 3: Audio Generation (Google TTS)**
    - Generate the audio for each scene.
4.  **Step 4: Assembly (n8n + Shotstack/Remotion)**
    - Overlay the audio on the image for each scene and stitch them together.

---

## 3. How to Save Even More Money

- **Use Batch API**: Google Cloud offers a "Batch" mode for Gemini that is **50% cheaper** if you don't need the result instantly (takes up to 24 hours).
- **Free Tier First**: Google Cloud has a "Free Tier" that gives you a certain number of requests per day for free. Your 190€ credits only start being used *after* you exceed the free limit.
- **Imagen 3 "Fast" Mode**: Use the "Fast" generation mode instead of "High Quality" for background visuals. It's 3x cheaper and still looks great on mobile.

---

## 4. Deep Dive: Batch API & 300 Videos/Day

### What is the Batch API?
The **Batch API** is designed for high-volume, non-urgent tasks. Instead of waiting for a response in real-time (Online API), you send a file (JSONL) with hundreds of requests. Google processes them in the background.

*   **Cost**: 50% discount compared to the Online API.
*   **Speed**: Results are returned within 24 hours (usually much faster).
*   **Limits**: It has its own separate quota, meaning it doesn't "clog up" your real-time requests.

### Can you do 300 videos/day?
**Yes, but you must use Batching.** 
If you try to generate 300 videos (approx. 4,500 images and 300 scripts) using the standard "Online" API, you will likely hit **Rate Limits (429 Errors)**.

| Limit Type | Online API (Standard) | Batch API (Recommended) |
| :--- | :--- | :--- |
| **RPM (Requests Per Minute)** | ~60-120 (Low) | Unlimited (Queue-based) |
| **TPM (Tokens Per Minute)** | ~30k - 1M | Massive (Millions) |
| **Reliability** | High risk of timeouts | 100% success (Retries handled by Google) |

### The "300/Day" Strategy:
1.  **Morning (Batch Scripts)**: Upload a single `.jsonl` file to Vertex AI containing 300 prompts for Gemini 1.5 Flash.
2.  **Afternoon (Batch Images)**: Once scripts are ready, extract the 4,500 image prompts and send them to the Imagen Batch API.
3.  **Evening (Assembly)**: Use a script or n8n to download all assets and render the videos.

---

## 5. Отладка и Тестирование (Перед запуском 300 шт)

**Важно:** Не запускай Batch на 300 видео, пока не проверишь промпты на 1-5 примерах. Иначе есть риск получить 300 роликов с "ахинеей".

### Сколько можно запускать по одному (Online API)?
Для тестов используй обычный (Online) API. Он работает мгновенно.

*   **Gemini 1.5 Flash**: До 15 запросов в минуту (бесплатно) или до 2000 (платно). Для отладки 5-10 сценариев этого более чем достаточно.
*   **Imagen 3**: Около 120 изображений в минуту.

### Пошаговый план проверки качества:
1.  **Тест Сценария (1-3 шт)**:
    *   Запусти промпт из `google_templates.json` в консоли Vertex AI.
    *   Проверь: Логичен ли текст? Не слишком ли он "роботизированный"?
    *   Если плохо — меняй `system_prompt`.
2.  **Тест Визуала (5-10 картинок)**:
    *   Возьми `image_prompt`, который сгенерировал Gemini, и вставь в Imagen 3.
    *   Проверь: Соответствует ли картинка тексту? Соблюдается ли стиль (например, Pixar или Cinematic)?
3.  **Тест Голоса**:
    *   Прослушай 2-3 фрагмента в Google TTS. Если голос слишком скучный, смени `voice_name` (например, на `en-US-Studio-O`).

### Когда переходить на Batch?
Только когда ты получил **3 идеальных видео подряд** в ручном режиме. Batch — это просто "умножитель" твоего успеха. Если ручной промпт плохой, Batch сделает 300 плохих видео.

---

## 6. Verification (Is it working?)

1.  **Prompt Test**: Run one prompt in the Vertex AI console. Does it return a valid JSON list of scenes?
2.  **Style Test**: Generate 3 images for the same video. Do they look like they belong to the same "style"? (Use a "Style Prompt" like *'Cinematic, 3D render, Pixar style'* in every prompt).
3.  **Credit Check**: Monitor your "Billing" dashboard in Google Cloud to ensure you are using the "Credits" and not your actual bank card.
