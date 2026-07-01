import { NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';

export const maxDuration = 60; // Allow more time for generation

async function getVertexToken() {
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON) {
    throw new Error('GOOGLE_APPLICATION_CREDENTIALS_JSON is not set');
  }
  const credentials = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON);
  const auth = new GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/cloud-platform']
  });
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  return { token: token.token, projectId: credentials.project_id };
}

export async function POST(req: Request) {
  try {
    const { topic, slideCount, referenceImage, chatHistory, currentDraft } = await req.json();

    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    const { token, projectId } = await getVertexToken();
    const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/gemini-1.5-pro-002:generateContent`;

    const n = slideCount || 6;
    let systemInstruction = `You are a world-class social media copywriter and visual designer. Your task is to create a ${n}-slide Instagram/Telegram carousel.

COPYWRITING RULES:
- Slide 1 (HOOK): Must be provocative, controversial, or surprising. Use pattern interrupt. Make people STOP scrolling.
- Middle slides: Follow AIDA or PAS formula. Each slide = one clear idea. Use power words.
- Last slide (CTA): Clear next step. Create urgency or FOMO.
- All subtitle text must be in Russian. Be specific, not generic. Avoid corporate clichés.
- Max 8 words per subtitle. Every word must earn its place.

IMAGE PROMPT RULES for each slide:
- Write a cinematographic scene description in English
- Specify: lighting (e.g. "golden hour", "neon cyberpunk", "soft studio light"), mood, color palette (name 2-3 dominant colors), composition style (e.g. "minimalist", "abstract gradient", "luxury texture"), any relevant objects or shapes
- CRITICAL: zero text, zero letters, zero numbers in the image
- Example of a great prompt: "Abstract fluid art, deep ocean blue and electric purple gradient waves, cinematic bokeh light particles, luxury aesthetic, dark moody atmosphere, no text"

OUTPUT FORMAT:
Return ONLY a valid JSON array. No markdown, no explanation, just the array.
Each object must have exactly these fields:
- "title": short uppercase label (e.g. "HOOK", "БОЛЬ", "РЕШЕНИЕ", "СЕКРЕТ", "ВЫГОДА", "CTA")
- "subtitle": powerful Russian text (max 8 words)
- "imagePrompt": detailed English visual scene description (3-4 sentences)

Make exactly ${n} slides. Follow the structure: Hook → Pain → Agitation → Solution → Proof/Benefit → CTA.`;


    const contents: any[] = [];
    
    // Add the initial topic prompt
    const initialParts: any[] = [{ text: `Topic: "${topic}"` }];
    
    // If a reference image is provided, we pass it so Gemini can analyze the style
    if (referenceImage) {
      // referenceImage should be base64 data URL
      const base64Data = referenceImage.split(',')[1];
      const mimeType = referenceImage.split(';')[0].split(':')[1];
      initialParts.push({ text: `Please analyze the visual style of this reference image and make sure the "imagePrompt" you generate for each slide matches its aesthetic, mood, and color palette perfectly.` });
      initialParts.push({
        inlineData: {
          data: base64Data,
          mimeType: mimeType
        }
      });
    }

    contents.push({ role: "user", parts: initialParts });
    
    // Add chat history if exists
    if (chatHistory && Array.isArray(chatHistory)) {
      // If we have history, it means we are revising a draft. We should add the current draft to the context.
      contents.push({ role: "model", parts: [{ text: `Current Draft:\n${JSON.stringify(currentDraft)}` }] });
      
      // Append the actual chat history
      chatHistory.forEach((msg: any) => {
        contents.push({
          role: msg.role === 'user' ? 'user' : 'model',
          parts: [{ text: msg.text }]
        });
      });
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemInstruction }] },
        contents: contents,
        generationConfig: {
          responseMimeType: "application/json",
          temperature: 0.7,
        }
      })
    });

    if (!response.ok) {
      const err = await response.text();
      console.error('Gemini error:', err);
      return NextResponse.json({ error: 'Failed to generate text' }, { status: 500 });
    }

    const data = await response.json();
    const textRes = data.predictions?.[0]?.content || data.candidates?.[0]?.content?.parts?.[0]?.text;
    
    if (!textRes) {
      return NextResponse.json({ error: 'No text returned' }, { status: 500 });
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
    return NextResponse.json({ error: 'Failed to generate draft' }, { status: 500 });
  }
}
