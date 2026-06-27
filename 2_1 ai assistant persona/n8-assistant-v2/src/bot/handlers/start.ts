import { Context } from "grammy";
import { createClient } from "../../utils/supabase/server";

export async function startHandler(ctx: Context) {
  const userId = ctx.from?.id;
  const username = ctx.from?.username;
  const firstName = ctx.from?.first_name;

  if (!userId) {
    await ctx.reply("Ошибка: не удалось определить пользователя.");
    return;
  }

  // Проверяем referral param: /start ref_12345
  const refParam = ctx.match?.toString() || "";
  let referrerId: number | null = null;
  if (refParam.startsWith("ref_")) {
    referrerId = parseInt(refParam.replace("ref_", ""), 10);
  }

  try {
    const supabase = await createClient();

    // Проверяем, есть ли уже пользователь
    const { data: existingUser } = await supabase
      .from("users")
      .select("id, credits_balance")
      .eq("telegram_id", userId)
      .single();

    if (existingUser) {
      await ctx.reply(
        `С возвращением, ${firstName || "друг"}! 👋\n\n` +
          `💰 Баланс: ${existingUser.credits_balance} CR\n` +
          `Что будем делать? Просто отправь голосовое, фото или текст.`
      );
      return;
    }

    // Создаём нового пользователя
    const { data: newUser, error } = await supabase
      .from("users")
      .insert({
        telegram_id: userId,
        telegram_username: username,
        display_name: firstName,
        credits_balance: 50, // Стартовые кредиты
        role: "user",
      })
      .select("id")
      .single();

    if (error) {
      console.error("Error creating user:", error);
      await ctx.reply("Произошла ошибка при регистрации. Попробуй позже.");
      return;
    }

    // Если это реферал — начисляем бонусы
    if (referrerId && referrerId !== userId) {
      await supabase.from("referrals").insert({
        referrer_id: referrerId,
        referred_id: userId,
        level: 1,
        bonus_credits: 50,
        commission_rate: 10,
      });

      // Бонус рефереру
      await supabase.rpc("add_credits", {
        user_telegram_id: referrerId,
        amount: 10, // 20% от стартовых 50
      });

      // Бонус рефералу
      await supabase.rpc("add_credits", {
        user_telegram_id: userId,
        amount: 50,
      });

      await ctx.reply(
        `🎉 Добро пожаловать, ${firstName || "друг"}!\n\n` +
          `Ты пришёл по реферальной ссылке. Получил +50 CR бонус!\n` +
          `💰 Баланс: 50 CR\n\n` +
          `Отправь голосовое, фото или текст — я помогу!`
      );
      return;
    }

    await ctx.reply(
      `🎉 Добро пожаловать, ${firstName || "друг"}!\n\n` +
        `Твой личный AI-сотрудник готов к работе.\n` +
        `💰 Ты получил 50 CR бесплатно.\n\n` +
        `Что я умею:\n` +
        `🎤 Голосовые → расшифровка\n` +
        `🖼️ Фото → анализ\n` +
        `📝 Текст → AI-ответ\n` +
        `🔗 YouTube → саммари\n\n` +
        `Напиши /ref чтобы получить реферальную ссылку и заработать больше кредитов!`
    );
  } catch (err) {
    console.error("Start handler error:", err);
    await ctx.reply("Произошла ошибка. Попробуй позже.");
  }
}
