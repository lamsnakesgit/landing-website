import { NextResponse } from 'next/server';
import { sendAdminNotification } from '@/lib/telegram';

export const maxDuration = 60;

// Фолбэк на Google AI Studio API (бесплатный Gemini API ключ)
async function generateWithGeminiAPI(systemInstruction: string, contents: any[]) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error('GEMINI_API_KEY is not set');

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=${apiKey}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: systemInstruction }] },
      contents: contents,
      generationConfig: {
        responseMimeType: 'application/json',
        temperature: 0.7,
      }
    })
  });

  if (!response.ok) {
    const err = await response.text();
    console.error('Gemini API error:', err);
    throw new Error('Gemini API failed: ' + err.substring(0, 200));
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('No text from Gemini API');
  return text;
}

// Vertex AI (когда SA доступен)
async function generateWithVertex(systemInstruction: string, contents: any[]) {
  const { GoogleAuth } = await import('google-auth-library');
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON) {
    throw new Error('GOOGLE_APPLICATION_CREDENTIALS_JSON is not set');
  }
  const credentials = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON);
  const auth = new GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/cloud-platform']
  });
  const client = await auth.getClient();
  const tokenRes = await client.getAccessToken();
  const token = tokenRes.token;
  const projectId = credentials.project_id;

  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: systemInstruction }] },
      contents,
      generationConfig: {
        responseMimeType: 'application/json',
        temperature: 0.7,
      }
    })
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error('Vertex failed: ' + err.substring(0, 200));
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('No text from Vertex');
  return text;
}

export async function POST(req: Request) {
  try {
    const { topic, slideCount, referenceImage, chatHistory, currentDraft } = await req.json();

    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }
    
    // Log to admin
    console.log(`📝 Генерация Черновика\nТема: ${topic}\nСлайдов: ${slideCount}\nС чатом? ${chatHistory?.length ? 'Да' : 'Нет'}`);

    const n = slideCount || 6;
    const systemInstruction = `Вы — топовый копирайтер и арт-директор. Ваша задача — создать карусель для Instagram/Telegram на ${n} слайдов.

ПРАВИЛА КОПИРАЙТИНГА:
- Слайд 1 (ХУК): Провокация, разрыв шаблона, неожиданный факт. Заставьте человека остановиться.
- Слайды 2-${n - 1}: Раскройте тему глубоко. Используйте формулу AIDA или PAS. Пишите ёмко, используйте сильные глаголы. Никакой воды и корпоративных штампов.
- Слайд ${n} (CTA): Четкий призыв к действию (подписка, комментарий, переход по ссылке). Создайте срочность.
- Текст должен быть на русском языке. Звучать естественно, экспертно и интригующе.

ПРАВИЛА ГЕНЕРАЦИИ ВИЗУАЛА (imagePrompt):
- Опишите визуальную сцену на АНГЛИЙСКОМ языке (для нейросети).
- Это ТЗ для дизайнера. Описывайте конкретно: композицию, освещение ("cinematic lighting", "neon glow"), цветовую палитру (2-3 цвета), текстуры, атмосферу.
- Избегайте текста на картинках. Фокусируйтесь на абстракциях, метафорах или высококачественных фотореалистичных объектах.
- Пример: "Minimalist abstract 3d rendering, glassmorphism UI elements floating in dark space, deep purple and electric blue gradient background, soft cinematic studio lighting, premium luxury aesthetic, 8k resolution, highly detailed."

ФОРМАТ ОТВЕТА (ВЕРНИТЕ ТОЛЬКО JSON ARRAY):
[
  {
    "title": "ХУК", 
    "subtitle": "Основной броский заголовок слайда (до 10 слов)",
    "body": "Раскрывающий текст слайда, который можно разместить ниже или сказать голосом. 2-3 предложения конкретики. Раскройте мысль глубже.",
    "imagePrompt": "Детальное ТЗ для визуала на английском языке (3-4 предложения)"
  }
]
Структура: Hook → Pain → Agitation → Solution → Proof/Benefit → CTA. Сделайте ровно ${n} слайдов.`;

    const contents: any[] = [];
    const initialParts: any[] = [{ text: `Topic: "${topic}"` }];

    if (referenceImage) {
      const base64Data = referenceImage.split(',')[1];
      const mimeType = referenceImage.split(';')[0].split(':')[1];
      initialParts.push({ text: `Analyze the visual style of this reference image and make "imagePrompt" for each slide match its aesthetic, mood, and color palette.` });
      initialParts.push({ inlineData: { data: base64Data, mimeType } });
    }

    contents.push({ role: 'user', parts: initialParts });

    if (chatHistory && Array.isArray(chatHistory) && chatHistory.length > 0) {
      contents.push({ role: 'model', parts: [{ text: `Current Draft:\n${JSON.stringify(currentDraft)}` }] });
      chatHistory.forEach((msg: any) => {
        contents.push({
          role: msg.role === 'user' ? 'user' : 'model',
          parts: [{ text: msg.text }]
        });
      });
    }

    // Пробуем Vertex, фолбэк на Gemini API
    let textRes: string;
    try {
      textRes = await generateWithVertex(systemInstruction, contents);
      console.log('Using Vertex AI');
    } catch (vertexErr) {
      console.warn('Vertex failed, falling back to Gemini API:', vertexErr);
      textRes = await generateWithGeminiAPI(systemInstruction, contents);
      console.log('Using Gemini API fallback');
    }

    let parsedDraft;
    try {
      parsedDraft = JSON.parse(textRes);
    } catch (e) {
      const cleaned = textRes.replace(/```json/g, '').replace(/```/g, '').trim();
      parsedDraft = JSON.parse(cleaned);
    }

    return NextResponse.json({ draft: parsedDraft });

  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
