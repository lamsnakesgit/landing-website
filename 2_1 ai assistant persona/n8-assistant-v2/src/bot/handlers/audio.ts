import { Context } from "grammy";
import { transcribeAudio } from "../services/transcription";

export async function audioHandler(ctx: Context) {
  const audio = ctx.message?.audio;
  if (!audio) return;

  const duration = audio.duration;
  const minutes = Math.floor(duration / 60);
  const seconds = duration % 60;

  const processingMsg = await ctx.reply(
    `📎 Получил аудиофайл: ${audio.file_name || "без названия"} (${minutes}:${seconds.toString().padStart(2, "0")})\nОбрабатываю...`
  );

  try {
    const file = await ctx.api.getFile(audio.file_id);
    const filePath = file.file_path;
    if (!filePath) {
      await ctx.api.editMessageText(
        ctx.chat!.id,
        processingMsg.message_id,
        "❌ Не удалось получить файл."
      );
      return;
    }

    const fileUrl = `https://api.telegram.org/file/bot${process.env.TELEGRAM_BOT_TOKEN}/${filePath}`;

    const transcription = await transcribeAudio(fileUrl);

    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      `📝 **Транскрипция аудио:**\n\n${transcription}\n\n_Длительность: ${minutes}:${seconds.toString().padStart(2, "0")}_`,
      { parse_mode: "Markdown" }
    );
  } catch (err) {
    console.error("Audio handler error:", err);
    await ctx.api.editMessageText(
      ctx.chat!.id,
      processingMsg.message_id,
      "❌ Ошибка при обработке аудио. Попробуй ещё раз."
    );
  }
}
