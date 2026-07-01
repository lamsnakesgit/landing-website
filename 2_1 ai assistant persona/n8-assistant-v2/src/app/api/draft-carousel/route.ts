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

    let systemInstruction = `You are an expert copywriter and AI designer. Create a ${slideCount || 6}-slide carousel structure for an Instagram/Telegram post.
    Return ONLY a valid JSON array. Each object in the array must have exactly:
    - "title": A very short punchy uppercase category (e.g. "HOOK", "БОЛЬ", "РЕШЕНИЕ", "СЕКРЕТ", "ВЫГОДА", "CTA").
    - "subtitle": A bold catchy text (max 6-8 words) in Russian.
    - "imagePrompt": A highly detailed prompt in English for an AI image generator to create an abstract, clean, cinematic background without any text.
    Make exactly ${slideCount || 6} slides.`;

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
