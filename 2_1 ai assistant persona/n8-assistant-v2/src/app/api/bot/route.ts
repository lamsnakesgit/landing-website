import { NextResponse } from 'next/server';

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
      // Если это просто текст, воспринимаем это как запрос на генерацию карусели
      // (В будущем здесь будет вызов n8n или Vertex AI)
      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_id: chatId,
          text: `⚙️ Принято! Начинаю генерацию карусели на тему: "${text}"...\n\n(Пока это заглушка. Скоро здесь появятся 6 готовых слайдов!)`
        })
      });
    }

    return NextResponse.json({ status: 'ok' });
  } catch (error) {
    console.error('Error handling Telegram Webhook:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
