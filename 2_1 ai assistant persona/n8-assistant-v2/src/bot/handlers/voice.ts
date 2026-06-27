import { Context } from "grammy";
import { transcribeAudio } from "../services/transcription";

export async function voiceHandler(ctx: Context) {
  const voice = ctx.message?.voice;
  if (!voice) return;

  const processingMsg = await ctx.reply("🎤 Получил голосовое. Обрабатываю...");

  try {
    // Получаем file_id и скачиваем
    const file = await ctx.api.getFile(voice.file_id);
    const filePath = file.file_path;
    if (!filePath) {
      await ctx.api.editMessageText(
        ctx.chat!.id,
        processingMsg.message_id,
        "❌ Не удалось получить файл."
      );
      return;
    }

    // Скачиваем через Telegram API
    const fileUrl = `https://api.telegram.org/file/bot${process.env.TELEGRAM_BOT_TOKEN}/${filePath}`;

    // Транскрибируем через Whisper API
    const transcription = await transcribeAudio(fileUrl);

    // Отвечаем транскриптом
    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      `📝 **Распознано:**\n\n${transcription}\n\n_Что дальше? Могу ответить на это или помочь с задачей._`,
      { parse_mode: "Markdown" }
    );
  } catch (err) {
    console.error("Voice handler error:", err);
    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      "❌ Ошибка при обработке голосового. Попробуй ещё раз."
    );
  }
}
