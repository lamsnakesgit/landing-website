import { Bot, webhookCallback } from "grammy";
import { startHandler } from "./handlers/start";
import { voiceHandler } from "./handlers/voice";
import { audioHandler } from "./handlers/audio";
import { photoHandler } from "./handlers/photo";
import { textHandler } from "./handlers/text";
import { referHandler } from "./handlers/refer";

const token = process.env.TELEGRAM_BOT_TOKEN || "";
if (!token) {
  console.warn("⚠️ TELEGRAM_BOT_TOKEN is not set. Bot will not work.");
}

export const bot = new Bot(token || "123456:dummy_token_for_build");

// === Commands ===
bot.command("start", startHandler);
bot.command("ref", referHandler);
bot.command("credits", (ctx) =>
  ctx.reply("💰 Твой баланс: 50 CR\n\nПополнить: /topup")
);
bot.command("help", (ctx) =>
  ctx.reply(
    "🤖 AI Hands Assistant — твой AI-сотрудник\n\n" +
      "Команды:\n" +
      "/start — начало работы\n" +
      "/ref — реферальная ссылка\n" +
      "/credits — баланс кредитов\n" +
      "/settings — настройки\n" +
      "/help — эта справка\n\n" +
      "Просто отправь мне:\n" +
      "🎤 Голосовое сообщение — транскрибирую\n" +
      "📎 Аудиофайл — расшифрую\n" +
      "🖼️ Фото — проанализирую\n" +
      "📝 Текст — отвечу как AI\n" +
      "🔗 Ссылку на YouTube — сделаю саммари"
  )
);
bot.command("settings", (ctx) =>
  ctx.reply("⚙️ Настройки пока в разработке.\nСкоро можно будет задать свой системный промпт!")
);

// === Media handlers ===
bot.on(":voice", voiceHandler);
bot.on(":audio", audioHandler);
bot.on(":photo", photoHandler);

// === Text fallback ===
bot.on(":text", textHandler);

// === Error handler ===
bot.catch((err) => {
  console.error("Bot error:", err.error);
});

// === Next.js webhook handler ===
export const botWebhook = webhookCallback(bot, "std/http", {
  secretToken: process.env.TELEGRAM_WEBHOOK_SECRET,
});
