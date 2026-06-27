/**
 * Multi-LLM Router.
 * Приоритет: Google AI Studio (Gemini API) → Groq → Vertex AI → AIHubMix → OpenRouter
 *
 * Каждый провайдер проверяется на наличие API-ключа перед вызовом.
 * При ошибке — автоматический fallback к следующему провайдеру.
 * Все запросы логируются в llm_usage_logs (Supabase).
 */

interface LLMMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

interface LLMResult {
  content: string;
  tokens: { input: number; output: number };
}

interface LLMProvider {
  name: string;
  call(messages: LLMMessage[]): Promise<LLMResult>;
}

// ============================================================
// 1. Google AI Studio (Gemini API) — первичный, бесплатный tier
// ============================================================
class GoogleAIProvider implements LLMProvider {
  name = "google-ai-studio";
  model = "gemini-2.0-flash";

  async call(messages: LLMMessage[]) {
    const apiKey = process.env.GOOGLE_AI_STUDIO_API_KEY;
    if (!apiKey) throw new Error("GOOGLE_AI_STUDIO_API_KEY is not set");

    const systemMsg = messages.find((m) => m.role === "system");
    const chatMsgs = messages.filter((m) => m.role !== "system");
    const contents = chatMsgs.map((m) => ({
      role: m.role === "assistant" ? "model" : "user",
      parts: [{ text: m.content }],
    }));

    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents,
          systemInstruction: systemMsg ? { parts: [{ text: systemMsg.content }] } : undefined,
          generationConfig: { maxOutputTokens: 4096 },
          safetySettings: [
            { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_ONLY_HIGH" },
            { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_ONLY_HIGH" },
          ],
        }),
      }
    );

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Google AI Studio error: ${res.status} ${text}`);
    }

    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
    return {
      content: text,
      tokens: {
        input: data.usageMetadata?.promptTokenCount || 0,
        output: data.usageMetadata?.candidatesTokenCount || 0,
      },
    };
  }
}

// ============================================================
// 2. Groq API — fallback 1 (бесплатно, 30 req/min)
// ============================================================
class GroqProvider implements LLMProvider {
  name = "groq";
  model = "llama-3.3-70b-versatile";

  async call(messages: LLMMessage[]) {
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) throw new Error("GROQ_API_KEY is not set");

    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: this.model, messages, max_tokens: 4096 }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Groq error: ${res.status} ${text}`);
    }

    const data = await res.json();
    return {
      content: data.choices?.[0]?.message?.content || "",
      tokens: {
        input: data.usage?.prompt_tokens || 0,
        output: data.usage?.completion_tokens || 0,
      },
    };
  }
}

// ============================================================
// 3. Vertex AI — fallback 2 (Google Cloud, service account)
// ============================================================
class VertexAIProvider implements LLMProvider {
  name = "vertex-ai";
  model = "gemini-2.0-flash";

  async call(messages: LLMMessage[]) {
    const projectId = process.env.VERTEX_AI_PROJECT_ID;
    const location = process.env.VERTEX_AI_LOCATION || "us-central1";
    const serviceAccountKey = process.env.VERTEX_AI_SERVICE_ACCOUNT_KEY;
    if (!projectId || !serviceAccountKey) {
      throw new Error("VERTEX_AI_PROJECT_ID or VERTEX_AI_SERVICE_ACCOUNT_KEY is not set");
    }

    const accessToken = await this.getAccessToken(serviceAccountKey);
    const systemMsg = messages.find((m) => m.role === "system");
    const chatMsgs = messages.filter((m) => m.role !== "system");
    const contents = chatMsgs.map((m) => ({
      role: m.role === "assistant" ? "model" : "user",
      parts: [{ text: m.content }],
    }));

    const endpoint = `https://${location}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${location}/publishers/google/models/${this.model}:generateContent`;

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        contents,
        systemInstruction: systemMsg ? { parts: [{ text: systemMsg.content }] } : undefined,
        generationConfig: { maxOutputTokens: 4096 },
      }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Vertex AI error: ${res.status} ${text}`);
    }

    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
    return {
      content: text,
      tokens: {
        input: data.usageMetadata?.promptTokenCount || 0,
        output: data.usageMetadata?.candidatesTokenCount || 0,
      },
    };
  }

  private async getAccessToken(serviceAccountKey: string): Promise<string> {
    // Vertex AI требует google-auth-library для OAuth2 через service account
    // В MVP используем Google AI Studio (бесплатно)
    throw new Error("Vertex AI требует google-auth-library. Используй Google AI Studio для MVP.");
  }
}

// ============================================================
// 4. AIHubMix — fallback 3 (free Gemini / GPT-4o-mini)
// ============================================================
class AIHubMixProvider implements LLMProvider {
  name = "aihubmix";
  model = "gemini-2.0-flash-exp-free";

  async call(messages: LLMMessage[]) {
    const apiKey = process.env.AIHUBMIX_API_KEY;
    if (!apiKey) throw new Error("AIHUBMIX_API_KEY is not set");

    const res = await fetch("https://aihubmix.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: this.model, messages, max_tokens: 4096 }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`AIHubMix error: ${res.status} ${text}`);
    }

    const data = await res.json();
    return {
      content: data.choices?.[0]?.message?.content || "",
      tokens: {
        input: data.usage?.prompt_tokens || 0,
        output: data.usage?.completion_tokens || 0,
      },
    };
  }
}

// ============================================================
// 5. OpenRouter — fallback 4 (универсальный, платный)
// ============================================================
class OpenRouterProvider implements LLMProvider {
  name = "openrouter";
  model = "google/gemini-2.0-flash-001";

  async call(messages: LLMMessage[]) {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) throw new Error("OPENROUTER_API_KEY is not set");

    const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: this.model, messages, max_tokens: 4096 }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`OpenRouter error: ${res.status} ${text}`);
    }

    const data = await res.json();
    return {
      content: data.choices?.[0]?.message?.content || "",
      tokens: {
        input: data.usage?.prompt_tokens || 0,
        output: data.usage?.completion_tokens || 0,
      },
    };
  }
}

// ============================================================
// Список провайдеров в порядке приоритета
// ============================================================
const providers: LLMProvider[] = [
  new GoogleAIProvider(),
  new GroqProvider(),
  new VertexAIProvider(),
  new AIHubMixProvider(),
  new OpenRouterProvider(),
];

/**
 * Вызывает LLM с автоматическим fallback между провайдерами.
 * Порядок: Google AI Studio → Groq → Vertex AI → AIHubMix → OpenRouter
 */
export async function callLLM(messages: LLMMessage[]): Promise<string> {
  let lastError: Error | null = null;

  for (const provider of providers) {
    try {
      // Проверка настроек провайдера
      if (provider instanceof GoogleAIProvider && !process.env.GOOGLE_AI_STUDIO_API_KEY) continue;
      if (provider instanceof GroqProvider && !process.env.GROQ_API_KEY) continue;
      if (provider instanceof VertexAIProvider && !process.env.VERTEX_AI_PROJECT_ID) continue;
      if (provider instanceof AIHubMixProvider && !process.env.AIHUBMIX_API_KEY) continue;
      if (provider instanceof OpenRouterProvider && !process.env.OPENROUTER_API_KEY) continue;

      console.log(`[LLM] Trying provider: ${provider.name}`);
      const result = await provider.call(messages);

      // Логируем usage
      logUsage(provider.name, result.tokens).catch((e) =>
        console.warn("[LLM] Failed to log usage:", e)
      );

      return result.content;
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      console.warn(`[LLM] Provider ${provider.name} failed:`, lastError.message);
    }
  }

  throw lastError || new Error("All LLM providers failed");
}

/**
 * Логирование использования LLM в Supabase (не блокирует ответ).
 */
async function logUsage(provider: string, tokens: { input: number; output: number }) {
  try {
    const { createClient } = await import("../../utils/supabase/server");
    const supabase = await createClient();
    await supabase.from("llm_usage_logs").insert({
      provider,
      input_tokens: tokens.input,
      output_tokens: tokens.output,
      cost_usd: calculateCost(provider, tokens),
      created_at: new Date().toISOString(),
    });
  } catch {
    // Логирование не должно ломать основной поток
  }
}

/**
 * Примерная стоимость запроса в USD (приблизительно).
 */
function calculateCost(provider: string, tokens: { input: number; output: number }): number {
  const rates: Record<string, { input: number; output: number }> = {
    "google-ai-studio": { input: 0, output: 0 }, // бесплатно
    groq: { input: 0, output: 0 },               // бесплатно
    "vertex-ai": { input: 0.0001, output: 0.0004 },
    aihubmix: { input: 0, output: 0 },            // free tier
    openrouter: { input: 0.00015, output: 0.0006 },
  };
  const rate = rates[provider] || { input: 0.0001, output: 0.0004 };
  const inputCost = (tokens.input / 1000) * rate.input;
  const outputCost = (tokens.output / 1000) * rate.output;
  return parseFloat((inputCost + outputCost).toFixed(6));
}

