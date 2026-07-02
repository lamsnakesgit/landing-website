import { NextResponse } from 'next/server';
import { sendAdminNotification } from '@/lib/telegram';
import { supabase } from '@/lib/supabase';

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const WEB_APP_URL = 'https://n8-assistant-v2.vercel.app/dashboard';

export async function POST(req: Request) {
  try {
    const update = await req.json();

    // Ignore if not a message
    if (!update.message || !update.message.text) {
      return NextResponse.json({ status: 'ignored' });
    }

    const chatId = update.message.chat.id;
    const text = update.message.text;
    const username = update.message.from?.username || 'Unknown';
    const firstName = update.message.from?.first_name || '';

    // Log to Supabase
    await supabase.from('users').upsert(
      { telegram_id: chatId, username, first_name: firstName, updated_at: new Date() },
      { onConflict: 'telegram_id' }
    );
    await supabase.from('logs').insert({
      telegram_id: chatId,
      action: text.startsWith('/start') ? 'start' : 'message',
      metadata: { text }
    });

    // Log to admin
    await sendAdminNotification(`👤 **Юзер в боте:** @${username} (${firstName})\n💬 **Пишет:** ${text}`);

    // Handle /start command
    if (text.startsWith('/start')) {
      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_id: chatId,
          text: '👋 Привет! Я твой AI-сотрудник с руками.\n\nНажми на кнопку ниже, чтобы открыть Контент Завод и начать генерацию.',
          reply_markup: {
            inline_keyboard: [
              [
                {
                  text: '🚀 Открыть Приложение',
                  web_app: {
                    url: WEB_APP_URL
                  }
                }
              ]
            ]
          }
        })
      });
    } else {
      // Handle /carousel command (or plain text as a carousel prompt)
      let topicPrompt = text;
      if (text.startsWith('/carousel ')) {
        topicPrompt = text.replace('/carousel ', '').trim();
      } else if (text === '/carousel') {
        await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: chatId,
            text: 'Напишите тему карусели после команды, например:\n`/carousel Как набрать 1000 подписчиков в Telegram`',
            parse_mode: 'Markdown'
          })
        });
        return NextResponse.json({ status: 'ok' });
      }

      // Generate Draft immediately
      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: `⚙️ Пишу текст для карусели на тему: "${topicPrompt}"...\n\nОжидайте пару секунд!`
        })
      });

      // Call our own draft generation API
      // Note: We are hardcoding the URL to our own API
      const draftRes = await fetch(`${WEB_APP_URL.replace('/dashboard', '')}/api/draft-carousel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topicPrompt, slideCount: 6 })
      });

      if (!draftRes.ok) {
        throw new Error('Failed to generate draft');
      }

      const draftData = await draftRes.json();
      const draftText = draftData.draft.map((s: any, i: number) => `*Слайд ${i+1}:* ${s.title}\n_${s.subtitle}_\n`).join('\n');

      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: `✅ **Черновик готов:**\n\n${draftText}\nВсё отлично? Жмите кнопку ниже, чтобы сгенерировать ИИ-визуал (займёт ~1 минуту).`,
          parse_mode: 'Markdown',
          reply_markup: {
            inline_keyboard: [
              [
                { text: '🎨 Сгенерировать картинки', callback_data: `GENERATE_CAROUSEL_${topicPrompt.substring(0, 40)}` },
                { text: 'Внести правки (В Mini App)', web_app: { url: WEB_APP_URL } }
              ]
            ]
          }
        })
      });
    }

    return NextResponse.json({ status: 'ok' });
  } catch (error) {
    console.error('Error handling Telegram Webhook:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
