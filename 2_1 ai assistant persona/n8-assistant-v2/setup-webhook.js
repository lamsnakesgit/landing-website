const https = require('https');

const token = process.env.TELEGRAM_BOT_TOKEN || '8862889466:AAHSBf7YeOh39pNjgLtCj57zy6ozIvHzIc4';
const webhookUrl = 'https://n8-assistant-v2.vercel.app/api/bot';

const url = `https://api.telegram.org/bot${token}/setWebhook?url=${webhookUrl}`;

https.get(url, (res) => {
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  res.on('end', () => {
    console.log('Webhook setup response:', data);
  });
}).on('error', (err) => {
  console.log('Error setting webhook:', err.message);
});
