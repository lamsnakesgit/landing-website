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

async function generateText(projectId: string, token: string, topic: string) {
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/gemini-1.5-pro-002:generateContent`;
  
  const prompt = `Create a 6-slide carousel structure for an Instagram/Telegram post about: "${topic}".
  Return ONLY a valid JSON array. Each object in the array must have exactly:
  - "title": A very short punchy uppercase category (e.g. "HOOK", "БОЛЬ", "РЕШЕНИЕ", "СЕКРЕТ", "ВЫГОДА", "CTA").
  - "subtitle": A bold catchy text (max 6-8 words) in Russian.
  - "imagePrompt": A highly detailed prompt in English for an AI image generator to create an abstract, clean, cinematic background without any text.
  Make exactly 6 slides.`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: "application/json",
        temperature: 0.7,
      }
    })
  });

  if (!response.ok) {
    const err = await response.text();
    console.error('Gemini error:', err);
    throw new Error('Failed to generate text');
  }

  const data = await response.json();
  const textRes = data.predictions?.[0]?.content || data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!textRes) throw new Error('No text returned from Gemini');
  
  try {
    return JSON.parse(textRes);
  } catch (e) {
    // Sometimes there are markdown blocks
    const cleaned = textRes.replace(/\`\`\`json/g, '').replace(/\`\`\`/g, '').trim();
    return JSON.parse(cleaned);
  }
}

async function generateImage(projectId: string, token: string, prompt: string, isFast: boolean = false) {
  const model = isFast ? 'imagen-3.0-fast-generate-001' : 'imagen-3.0-generate-001';
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/${model}:predict`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      instances: [{ prompt: prompt + ", abstract, aesthetic, no text, no letters, cinematic lighting" }],
      parameters: {
        sampleCount: 1,
        aspectRatio: "3:4",
      }
    })
  });

  if (!response.ok) {
    const err = await response.text();
    console.error('Imagen error:', err);
    return null;
  }

  const data = await response.json();
  const base64 = data.predictions?.[0]?.bytesBase64Encoded;
  return base64 ? \`data:image/png;base64,\${base64}\` : null;
}

export async function POST(req: Request) {
  try {
    const { topic, modelChoice } = await req.json();

    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    const { token, projectId } = await getVertexToken();

    // 1. Generate text structure
    const carouselData = await generateText(projectId, token as string, topic);
    
    if (!Array.isArray(carouselData)) {
      throw new Error("Invalid format returned by Gemini");
    }

    // 2. Generate backgrounds
    const finalSlides = await Promise.all(carouselData.map(async (slide: any) => {
      let backgroundUrl = '';
      
      if (modelChoice === 'presentation') {
        // Fallback or empty, we will use dark solid color or random Unsplash abstract
        backgroundUrl = `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format`;
      } else {
        // Nano 2 (pro) or Nano Banana (flash/fast)
        const isFast = modelChoice === 'nano';
        const img = await generateImage(projectId, token as string, slide.imagePrompt, isFast);
        backgroundUrl = img || `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format`;
      }

      return {
        ...slide,
        backgroundUrl
      };
    }));

    return NextResponse.json({ slides: finalSlides });

  } catch (error: any) {
    console.error('Carousel generation error:', error);
    return NextResponse.json({ error: 'Failed to generate carousel' }, { status: 500 });
  }
}
