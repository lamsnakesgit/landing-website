/**
 * Сервис анализа и генерации изображений.
 * Использует Gemini Flash Vision (бесплатно) через Google AI Studio.
 */

const GOOGLE_AI_ENDPOINT =
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

/**
 * Анализирует изображение.
 * @param imageUrl - публичный URL изображения
 * @param userPrompt - дополнительный промпт от пользователя
 */
export async function analyzeImage(
  imageUrl: string,
  userPrompt: string = ""
): Promise<string> {
  const apiKey = process.env.GOOGLE_AI_STUDIO_API_KEY;
  if (!apiKey) {
    return "⚠️ Анализ изображений временно недоступен (не настроен API-ключ Google AI).";
  }

  const defaultPrompt =
    "Опиши, что ты видишь на этом изображении. Если есть текст — прочитай его. Ответь на русском языке, кратко и по делу.";

  const prompt = userPrompt || defaultPrompt;

  try {
    const response = await fetch(`${GOOGLE_AI_ENDPOINT}?key=${apiKey}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: prompt },
              {
                inline_data: {
                  mime_type: "image/jpeg",
                  data: await urlToBase64(imageUrl),
                },
              },
            ],
          },
        ],
        safetySettings: [
          { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_ONLY_HIGH" },
          { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_ONLY_HIGH" },
        ],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Google AI API error: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!text) {
      return "⚠️ Не удалось проанализировать изображение.";
    }

    return text;
  } catch (err) {
    console.error("Image analysis error:", err);
    return "⚠️ Ошибка при анализе изображения. Попробуй ещё раз.";
  }
}

/**
 * Генерирует изображение по промпту.
 */
export async function generateImage(prompt: string): Promise<string | null> {
  // Используем OpenRouter для генерации
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) return null;

  try {
    const response = await fetch(
      "https://openrouter.ai/api/v1/chat/completions",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "stabilityai/stable-diffusion-3.5",
          messages: [{ role: "user", content: prompt }],
        }),
      }
    );

    if (!response.ok) return null;

    const data = await response.json();
    return data.choices?.[0]?.message?.content || null;
  } catch (err) {
    console.error("Image generation error:", err);
    return null;
  }
}

/**
 * Конвертирует URL изображения в base64
 */
async function urlToBase64(url: string): Promise<string> {
  const response = await fetch(url);
  const blob = await response.blob();
  const buffer = await blob.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary);
}
