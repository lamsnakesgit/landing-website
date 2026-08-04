import { Context } from "grammy";
import { createClient } from "../../utils/supabase/server";

export async function referHandler(ctx: Context) {
  const userId = ctx.from?.id;
  if (!userId) {
    await ctx.reply("❌ Ошибка: не удалось определить пользователя.");
    return;
  }

  try {
    const supabase = await createClient();

    // Статистика рефералов
    const { data: referrals } = await supabase
      .from("referrals")
      .select("level, created_at")
      .eq("referrer_id", userId)
      .order("created_at", { ascending: false });

    const level1 = referrals?.filter((r) => r.level === 1).length || 0;
    const level2 = referrals?.filter((r) => r.level === 2).length || 0;
    const level3 = referrals?.filter((r) => r.level === 3).length || 0;

    // Заработано кредитов
    const { data: earnings } = await supabase
      .from("referral_earnings")
      .select("amount")
      .eq("user_id", userId)
      .eq("status", "available");

    const totalEarned = earnings?.reduce((sum, e) => sum + Number(e.amount), 0) || 0;

    const refLink = `https://t.me/${process.env.TELEGRAM_BOT_USERNAME || "aihandsworkcontentbot"}?start=ref_${userId}`;

    await ctx.reply(
      `🔗 **Твоя реферальная ссылка:**\n\`${refLink}\`\n\n` +
        `👥 **Приглашено:**\n` +
        `  • Уровень 1: ${level1} чел.\n` +
        `  • Уровень 2: ${level2} чел.\n` +
        `  • Уровень 3: ${level3} чел.\n\n` +
        `💰 **Заработано:** ${totalEarned} CR\n` +
        `_Мин. вывод: 1000 CR_\n\n` +
        `**За каждую регистрацию:**\n` +
        `  • Ты: +20% от их стартовых кредитов\n` +
        `  • Они: +50 CR бонус\n\n` +
        `**С покупок:** L1: 10% | L2: 5% | L3: 2.5%`,
      { parse_mode: "Markdown", link_preview_options: { is_disabled: true } }
    );
  } catch (err) {
    console.error("Refer handler error:", err);
    await ctx.reply("❌ Ошибка загрузки реферальной информации.");
  }
}
