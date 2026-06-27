import { botWebhook } from "@/bot/index";

/**
 * Webhook endpoint для Telegram Bot.
 * POST /api/bot — Telegram шлёт сюда updates
 */
export async function POST(request: Request) {
  try {
    const response = await botWebhook(request);
    return response;
  } catch (err) {
    console.error("Webhook error:", err);
    return new Response("Webhook error", { status: 500 });
  }
}

/**
 * GET /api/bot — проверка что бот работает
 */
export async function GET() {
  return new Response(
    JSON.stringify({ status: "ok", bot: "n8-assistant-bot" }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}
