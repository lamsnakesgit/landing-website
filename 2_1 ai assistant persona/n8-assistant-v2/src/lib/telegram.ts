const ADMIN_NOTIFICATION_DEDUP_MS = 60_000;
const ADMIN_NOTIFICATION_MIN_INTERVAL_MS = 1_200;
const MAX_DEDUP_CACHE_SIZE = 200;

const recentAdminNotifications = new Map<string, number>();
let lastAdminNotificationAt = 0;

function normalizeAdminMessage(message: string) {
  return message
    .replace(/\d{2}:\d{2}:\d{2}/g, '<time>')
    .replace(/\d{4}-\d{2}-\d{2}[^\s]*/g, '<date>')
    .replace(/[a-f0-9-]{24,}/gi, '<id>')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 500);
}

function rememberNotification(key: string, now: number) {
  recentAdminNotifications.set(key, now);

  if (recentAdminNotifications.size > MAX_DEDUP_CACHE_SIZE) {
    const oldestKey = recentAdminNotifications.keys().next().value;
    if (oldestKey) recentAdminNotifications.delete(oldestKey);
  }
}

export async function sendAdminNotification(message: string) {
  const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID;

  if (!TELEGRAM_BOT_TOKEN || !ADMIN_CHAT_ID) {
    console.warn('Telegram notifications skipped: TELEGRAM_BOT_TOKEN or ADMIN_CHAT_ID not set');
    return;
  }

  const now = Date.now();
  const dedupKey = normalizeAdminMessage(message);
  const previousSentAt = recentAdminNotifications.get(dedupKey);

  if (previousSentAt && now - previousSentAt < ADMIN_NOTIFICATION_DEDUP_MS) {
    console.warn('[Telegram] Duplicate admin notification skipped');
    return;
  }

  if (now - lastAdminNotificationAt < ADMIN_NOTIFICATION_MIN_INTERVAL_MS) {
    console.warn('[Telegram] Admin notification throttled');
    return;
  }

  rememberNotification(dedupKey, now);
  lastAdminNotificationAt = now;

  try {
    const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
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

    if (!response.ok) {
      const errorText = await response.text();
      console.warn('[Telegram] Admin notification failed:', response.status, errorText.slice(0, 200));
    }
  } catch (error) {
    console.error('Failed to send admin notification:', error);
  }
}