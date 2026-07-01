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

async function generateImage(projectId: string, token: string, prompt: string, isFast: boolean = false, aspectRatio: string = "3:4") {
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
        aspectRatio: aspectRatio, // Options: "1:1", "9:16", "16:9", "3:4", "4:3"
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
  return base64 ? `data:image/png;base64,${base64}` : null;
}

export async function POST(req: Request) {
  try {
    const { slides, modelChoice, aspectRatio } = await req.json();

    if (!slides || !Array.isArray(slides)) {
      return NextResponse.json({ error: 'Valid slides array is required' }, { status: 400 });
    }

    const { token, projectId } = await getVertexToken();

    // Generate backgrounds for the approved draft
    const finalSlides = await Promise.all(slides.map(async (slide: any) => {
      let backgroundUrl = '';
      
      if (modelChoice === 'presentation') {
        // Fallback or empty, we will use dark solid color or random Unsplash abstract
        backgroundUrl = `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format`;
      } else {
        // Nano 2 (pro) or Nano Banana (flash/fast)
        const isFast = modelChoice === 'nano';
        // Map 4:5 to 3:4 for Imagen API since 4:5 is not directly supported by Imagen 3 standard aspect ratios
        let apiAspectRatio = aspectRatio;
        if (apiAspectRatio === '4:5') apiAspectRatio = '3:4';
        
        const img = await generateImage(projectId, token as string, slide.imagePrompt, isFast, apiAspectRatio);
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
    return NextResponse.json({ error: 'Failed to generate carousel images' }, { status: 500 });
  }
}
