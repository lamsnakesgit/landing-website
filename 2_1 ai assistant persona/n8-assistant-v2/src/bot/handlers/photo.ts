import { Context } from "grammy";
import { analyzeImage } from "../services/image";

export async function photoHandler(ctx: Context) {
  const photos = ctx.message?.photo;
  if (!photos || photos.length === 0) return;

  // Берём самое большое качество
  const bestPhoto = photos[photos.length - 1];

  const processingMsg = await ctx.reply("🖼️ Получил фото. Анализирую...");

  try {
    const file = await ctx.api.getFile(bestPhoto.file_id);
    const filePath = file.file_path;
    if (!filePath) {
      await ctx.api.editMessageText(
        ctx.chat!.id,
        processingMsg.message_id,
        "❌ Не удалось получить файл."
      );
      return;
    }

    const photoUrl = `https://api.telegram.org/file/bot${process.env.TELEGRAM_BOT_TOKEN}/${filePath}`;

    // Анализируем фото через Gemini Vision
    const analysis = await analyzeImage(photoUrl, ctx.message?.caption || "");

    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      `🔍 **Анализ фото:**\n\n${analysis}`,
      { parse_mode: "Markdown" }
    );
  } catch (err) {
    console.error("Photo handler error:", err);
    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      "❌ Ошибка при анализе фото. Попробуй ещё раз."
    );
  }
}
