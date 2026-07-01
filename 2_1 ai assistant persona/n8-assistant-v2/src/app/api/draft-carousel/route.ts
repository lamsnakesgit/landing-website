import { NextResponse } from 'next/server';

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

    const n = slideCount || 6;
    const systemInstruction = `You are a world-class social media copywriter and visual designer. Your task is to create a ${n}-slide Instagram/Telegram carousel.

COPYWRITING RULES:
- Slide 1 (HOOK): Must be provocative, controversial, or surprising. Use pattern interrupt. Make people STOP scrolling.
- Middle slides: Follow AIDA or PAS formula. Each slide = one clear idea. Use power words.
- Last slide (CTA): Clear next step. Create urgency or FOMO.
- All subtitle text must be in Russian. Be specific, not generic. Avoid corporate clichés.
- Max 8 words per subtitle. Every word must earn its place.

IMAGE PROMPT RULES for each slide (imagePrompt field):
- Write a cinematographic visual scene description in English
- Specify: lighting type (e.g. "golden hour", "neon cyberpunk", "soft studio light"), mood, color palette (2-3 dominant colors), composition (e.g. "minimalist", "abstract gradient", "luxury texture")
- Prefer abstract/atmospheric backgrounds without visible text or UI elements
- Example: "Abstract fluid art, deep ocean blue and electric purple gradient waves, cinematic bokeh light particles, luxury aesthetic, dark moody atmosphere"

OUTPUT FORMAT:
Return ONLY a valid JSON array. No markdown, no explanation.
Each object must have exactly:
- "title": short uppercase label (e.g. "HOOK", "БОЛЬ", "РЕШЕНИЕ", "СЕКРЕТ", "ВЫГОДА", "CTA")
- "subtitle": powerful Russian text (max 8 words)
- "imagePrompt": detailed English visual scene (3-4 sentences)

Make exactly ${n} slides. Structure: Hook → Pain → Agitation → Solution → Proof/Benefit → CTA.`;

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
    console.error('Draft generation error:', error);
    return NextResponse.json({ error: error.message || 'Failed to generate draft' }, { status: 500 });
  }
}
