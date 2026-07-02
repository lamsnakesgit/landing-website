export async function sendAdminNotification(message: string) {
  const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID;

  if (!TELEGRAM_BOT_TOKEN || !ADMIN_CHAT_ID) {
    console.warn('Telegram notifications skipped: TELEGRAM_BOT_TOKEN or ADMIN_CHAT_ID not set');
    return;
  }

  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: ADMIN_CHAT_ID,
        text: `🛡 **ADMIN LOG**\n\n${message}`,
        parse_mode: 'Markdown'
      })
    });
  } catch (error) {
    console.error('Failed to send admin notification:', error);
  }
}
