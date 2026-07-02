import { NextResponse } from 'next/server';

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

export async function POST(req: Request) {
  try {
    const { chatId, images, topic } = await req.json();

    if (!chatId || !images || !Array.isArray(images)) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    if (!TELEGRAM_BOT_TOKEN) {
      return NextResponse.json({ error: 'Bot token not configured' }, { status: 500 });
    }

    // Send images one by one (or as media group, but base64 upload is easier one by one in Node.js fetch)
    for (let i = 0; i < images.length; i++) {
      const base64Data = images[i].replace(/^data:image\/\w+;base64,/, "");
      const buffer = Buffer.from(base64Data, 'base64');
      
      const formData = new FormData();
      formData.append('chat_id', chatId.toString());
      formData.append('photo', new Blob([buffer], { type: 'image/png' }), `slide_${i}.png`);
      
      if (i === 0) {
        formData.append('caption', `🎨 Ваша карусель на тему: ${topic || 'Без темы'}`);
      }

      const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendPhoto`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const err = await res.text();
        console.error('Failed to send photo to Telegram:', err);
      }
      
      // Small delay to prevent rate limits
      await new Promise(r => setTimeout(r, 500));
    }

    return NextResponse.json({ success: true });

  } catch (error: any) {
    console.error('Send images error:', error);
    return NextResponse.json({ error: 'Failed to send images' }, { status: 500 });
  }
}
