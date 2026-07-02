import { NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';
import { sendAdminNotification } from '@/lib/telegram';
import { supabase } from '@/lib/supabase';
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

async function generateImage(projectId: string, token: string, prompt: string, modelChoice: string = 'nano-banana-1', aspectRatio: string = "3:4", referenceImageBase64?: string) {
  // Nano Banana 1 uses flash-image, Nano Banana 2 (pro) could use pro-image, but user asks for nano-banana-2
  const model = modelChoice === 'nano-banana-2' ? 'gemini-3-pro-image' : 'gemini-3.1-flash-image';
  
  // MUST use global endpoint for gemini-3.1-flash-image / gemini-3-pro-image
  const url = `https://aiplatform.googleapis.com/v1/projects/${projectId}/locations/global/publishers/google/models/${model}:generateContent`;
  
  const parts: any[] = [{ text: prompt }];
  if (referenceImageBase64) {
    const base64Data = referenceImageBase64.replace(/^data:image\/\w+;base64,/, '');
    const mimeType = referenceImageBase64.match(/^data:(image\/\w+);base64,/)?.[1] || 'image/jpeg';
    parts.push({
      inlineData: {
        mimeType,
        data: base64Data
      }
    });
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [{
        role: "user",
        parts
      }],
      generationConfig: {
        responseModalities: ["IMAGE"],
        temperature: 1.0,
      }
    })
  });

  if (!response.ok) {
    const err = await response.text();
    console.error('Nano Banana Vertex error:', err);
    throw new Error(`Nano Banana API failed: ${response.statusText} - ${err.substring(0, 200)}`);
  }

  const data = await response.json();
  const base64 = data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
  const mimeTypeRes = data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.mimeType || 'image/jpeg';
  
  return base64 ? `data:${mimeTypeRes};base64,${base64}` : null;
}

export async function POST(req: Request) {
  try {
    const { slides, modelChoice, aspectRatio, imageStyle, referenceImage, telegramId } = await req.json();

    if (!slides || !Array.isArray(slides)) {
      return NextResponse.json({ error: 'Valid slides array is required' }, { status: 400 });
    }

    if (telegramId) {
      await supabase.from('logs').insert({
        telegram_id: telegramId,
        action: 'generate_carousel',
        metadata: { modelChoice, slidesCount: slides.length }
      });
    }

    // Log to admin
    await sendAdminNotification(`🎨 **Рендеринг Дизайна**\n**Модель:** ${modelChoice}\n**Формат:** ${aspectRatio}\n**Слайдов:** ${slides.length}`);

    const { token, projectId } = await getVertexToken();

    // Process each slide sequentially (or parallel, but Gemini might have rate limits)
    const finalSlides = await Promise.all(slides.map(async (slide: any) => {
      let backgroundUrl = slide.backgroundUrl || '';
      
      if (!backgroundUrl) {
        if (modelChoice === 'presentation') {
           backgroundUrl = `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format`;
        } else {
          // Here we build the prompt including the user's style preference
          let promptWithStyle = slide.imagePrompt;
          if (imageStyle) {
            promptWithStyle += `\n\nVisual Style and Target Audience: ${imageStyle}`;
          }
          const aspectPrompt = `\n\nGenerate this image in ${aspectRatio} aspect ratio.`;
          const img = await generateImage(projectId, token as string, promptWithStyle + aspectPrompt, modelChoice, aspectRatio, referenceImage);
          backgroundUrl = img || `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format`;
        }
      }

      return {
        ...slide,
        backgroundUrl
      };
    }));

    return NextResponse.json({ slides: finalSlides });

  } catch (error: any) {
    console.error('Carousel generation error:', error);
    await sendAdminNotification(`❌ **Ошибка Рендеринга**\n\`${error.message || 'Unknown error'}\``);
    return NextResponse.json({ error: 'Failed to generate carousel' }, { status: 500 });
  }
}
