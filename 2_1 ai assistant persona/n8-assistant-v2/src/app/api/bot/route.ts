import { NextResponse } from 'next/server';
import { sendAdminNotification } from '@/lib/telegram';
import { supabase } from '@/lib/supabase';
import { Nango } from '@nangohq/node';

const nango = new Nango({ secretKey: process.env.NANGO_SECRET_KEY || 'dummy_for_build' });

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const WEB_APP_URL = 'https://n8-assistant-v2.vercel.app/dashboard';
const ADMIN_ID = 888005446;

async function sendTelegramMessage(chatId: number, text: string, replyMarkup?: object) {
  await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: 'Markdown',
      reply_markup: replyMarkup,
    }),
  });
}

const MAIN_MENU = {
  inline_keyboard: [
    [{ text: '🚀 Открыть Контент Завод', web_app: { url: WEB_APP_URL } }],
    [{ text: '🔗 Подключить сервисы (Google/Notion)', callback_data: 'connect_menu' }],
    [{ text: '👤 Мой профиль & токены', callback_data: 'profile' }],
    [{ text: '🔗 Моя реф-ссылка', callback_data: 'referral' }],
  ],
};

const CONNECT_MENU = {
  inline_keyboard: [
    [{ text: '📅 Google Calendar', callback_data: 'connect_google-calendar' }],
    [{ text: '📝 Google Docs', callback_data: 'connect_google-docs' }],
    [{ text: '🎯 Notion', callback_data: 'connect_notion' }],
    [{ text: '◀️ Назад', callback_data: 'main_menu' }],
  ],
};

export async function POST(req: Request) {
  try {
    const update = await req.json();

    // Обработка инлайн-кнопок
    if (update.callback_query) {
      const { id, data, from, message } = update.callback_query;
      const chatId = message.chat.id;

      fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/answerCallbackQuery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ callback_query_id: id }),
      }).catch(console.error);

      if (data === 'main_menu') {
        await sendTelegramMessage(chatId, 'Главное меню:', MAIN_MENU);
      } else if (data === 'connect_menu') {
        await sendTelegramMessage(chatId, '🔗 Выберите сервис для подключения:', CONNECT_MENU);
      } else if (data.startsWith('connect_')) {
        const provider = data.replace('connect_', '');
        try {
          const authUrl = `https://api.nango.dev/oauth/connect/${provider}?connection_id=${chatId}&public_key=${process.env.NANGO_PUBLIC_KEY || 'NANGO_PUBLIC_KEY_HERE'}`;
          await sendTelegramMessage(chatId, `🔗 Перейдите по ссылке для подключения *${provider}*:\n\n${authUrl}\n\n_(Ссылка активна только для вас)_`);
        } catch (e: any) {
          await sendTelegramMessage(chatId, `❌ Ошибка генерации ссылки. Убедитесь, что Nango настроен.`);
        }
      } else if (data === 'profile') {
        const { data: user } = await supabase.from('users').select('tokens, username, referred_by').eq('telegram_id', chatId).maybeSingle();
        const tokens = user?.tokens ?? 500;
        const ref = user?.referred_by ? `\n🤝 Приглашён пользователем: \`${user.referred_by}\`` : '';
        await sendTelegramMessage(chatId, `👤 *Ваш профиль:*\n\n🪙 Токены: *${tokens}*${ref}\n\nЗа каждую генерацию карусели списывается 1 токен.`);
      } else if (data === 'referral') {
        const refLink = `https://t.me/aihandsworkcontent_bot?start=ref_${chatId}`;
        await sendTelegramMessage(chatId, `🔗 *Ваша реф-ссылка:*\n\n\`${refLink}\`\n\nДелитесь с друзьями — вы получаете *50 токенов*!`);
        if (chatId !== ADMIN_ID) await sendAdminNotification(`🔗 @${from.username} запросил реф-ссылку`);
      } else if (data === 'draft_retry') {
        await supabase.from('users').update({ state: 'wait_topic' }).eq('telegram_id', chatId);
        await sendTelegramMessage(chatId, 'Напишите, что именно нужно изменить или добавить в черновик:');
      } else if (data === 'draft_cancel') {
        await supabase.from('users').update({ state: 'idle', state_data: null }).eq('telegram_id', chatId);
        await sendTelegramMessage(chatId, 'Генерация отменена.', MAIN_MENU);
      }

      return NextResponse.json({ status: 'ok' });
    }

    if (!update.message?.text) {
      return NextResponse.json({ status: 'ignored' });
    }

    const { chat, text, from } = update.message;
    const chatId: number = chat.id;
    const username = from?.username || 'Unknown';
    const firstName = from?.first_name || '';

    let referredBy: string | null = null;
    if (text.startsWith('/start ref_')) {
      referredBy = text.replace('/start ref_', '').trim();
    }

    const { data: existingUser } = await supabase.from('users').select('state, state_data, referred_by').eq('telegram_id', chatId).maybeSingle();

    const upsertData: Record<string, unknown> = {
      telegram_id: chatId,
      username,
      first_name: firstName,
      updated_at: new Date(),
    };
    if (referredBy && !existingUser?.referred_by) upsertData.referred_by = referredBy;

    await supabase.from('users').upsert(upsertData, { onConflict: 'telegram_id' });

    if (referredBy && !existingUser) {
      try {
        await supabase.rpc('increment_tokens', { p_telegram_id: Number(referredBy), p_amount: 50 });
      } catch (e) {}
    }

    await supabase.from('logs').insert({
      telegram_id: chatId,
      action: text.startsWith('/start') ? 'start' : 'message',
      metadata: { text },
    });

    if (chatId !== ADMIN_ID) {
      await sendAdminNotification(`👤 *@${username}* (${firstName})\n💬 ${text}`);
    }

    const userState = existingUser?.state || 'idle';

    if (text === '/cancel') {
      await supabase.from('users').update({ state: 'idle', state_data: null }).eq('telegram_id', chatId);
      await sendTelegramMessage(chatId, 'Действие отменено.', MAIN_MENU);
      return NextResponse.json({ status: 'ok' });
    }

    if (text.startsWith('/start')) {
      await supabase.from('users').update({ state: 'idle' }).eq('telegram_id', chatId);
      const greeting = referredBy ? `👋 Привет, ${firstName}! Тебя пригласил друг.\n\nВыбери действие:` : `👋 Привет, ${firstName}! Я твой AI-сотрудник с руками.\n\nВыбери действие:`;
      await sendTelegramMessage(chatId, greeting, MAIN_MENU);
    } else if (text === '/ref') {
      const refLink = `https://t.me/aihandsworkcontent_bot?start=ref_${chatId}`;
      await sendTelegramMessage(chatId, `🔗 *Ваша реф-ссылка:*\n\n\`${refLink}\`\n\nДелитесь с друзьями — вы получаете *50 токенов*!`);
    } else if (text === '/connect') {
      await supabase.from('users').update({ state: 'idle' }).eq('telegram_id', chatId);
      await sendTelegramMessage(chatId, '🔗 Выберите сервис для подключения:', CONNECT_MENU);
    } else if (text.startsWith('/carousel')) {
      await supabase.from('users').update({ state: 'wait_topic' }).eq('telegram_id', chatId);
      await sendTelegramMessage(chatId, '📝 *Новая карусель*\nНапишите тему для карусели или распишите подробно, о чём она должна быть:');
    } else if (userState === 'wait_topic') {
      await sendTelegramMessage(chatId, `⚙️ Пишу текст на тему: _"${text}"_...\n\nОжидайте!`);
      const draftRes = await fetch(`${WEB_APP_URL.replace('/dashboard', '')}/api/draft-carousel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: text, slideCount: 6 }),
      });

      if (!draftRes.ok) {
        await sendTelegramMessage(chatId, '❌ Не удалось сгенерировать черновик. Попробуйте позже.');
        await supabase.from('users').update({ state: 'idle' }).eq('telegram_id', chatId);
        return NextResponse.json({ status: 'ok' });
      }

      const draftData = await draftRes.json();
      await supabase.from('users').update({ state: 'review_draft', state_data: draftData }).eq('telegram_id', chatId);

      const draftText = draftData.draft.map((s: { title: string; subtitle: string }, i: number) => `*Слайд ${i + 1}:* ${s.title}\n_${s.subtitle}_`).join('\n\n');

      await sendTelegramMessage(
        chatId,
        `✅ *Черновик готов:*\n\n${draftText}\n\nВсё ок?`,
        {
          inline_keyboard: [
            [{ text: '✅ Утвердить и сгенерировать', web_app: { url: WEB_APP_URL } }],
            [{ text: '🔄 Изменить / Дополнить', callback_data: 'draft_retry' }],
            [{ text: '❌ Отмена', callback_data: 'draft_cancel' }]
          ],
        }
      );
    } else {
      await sendTelegramMessage(chatId, 'Напишите /start чтобы открыть меню или /carousel чтобы создать карусель.', MAIN_MENU);
    }

    return NextResponse.json({ status: 'ok' });
  } catch (error) {
    console.error('Ошибка в Telegram Webhook:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
// Force redeploy
// Force Vercel redeploy 2
