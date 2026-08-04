import { Context } from "grammy";
import { callLLM } from "../services/llm";

export async function textHandler(ctx: Context) {
  const text = ctx.message?.text;
  if (!text) return;

  // Игнорируем команды
  if (text.startsWith("/")) return;

  const processingMsg = await ctx.reply("🤔 Думаю...");

  try {
    const response = await callLLM([
      {
        role: "system",
        content:
          "Ты — AI Hands Assistant, дружелюбный AI-помощник. Отвечай кратко, по делу, на русском языке. Помогай с задачами, давай советы, генерируй идеи.",
      },
      {
        role: "user",
        content: text,
      },
    ]);

    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      response,
      { parse_mode: "Markdown" }
    );
  } catch (err) {
    console.error("Text handler error:", err);
    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      "❌ Ошибка обработки запроса. Попробуй ещё раз."
    );
  }
}
