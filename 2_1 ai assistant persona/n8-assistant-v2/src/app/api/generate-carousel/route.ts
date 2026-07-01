import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { topic, modelChoice } = await req.json();

    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    // 1. Сначала генерируем структуру карусели (JSON) через Gemini Text (или OpenAI)
    // Здесь мы просим ИИ придумать крутые заголовки и описания фонов.
    const carouselData = [
      {
        title: "HOOK",
        subtitle: "Как " + topic.substring(0, 20) + " изменит всё",
        imagePrompt: "neon cyberpunk city background, dark atmospheric, cinematic lighting, no text, clean composition"
      },
      {
        title: "БОЛЬ",
        subtitle: "Вы теряете время впустую",
        imagePrompt: "dark office background, moody lighting, abstract, no text"
      },
      {
        title: "РЕШЕНИЕ",
        subtitle: "Автоматизация за 5 минут",
        imagePrompt: "bright glowing abstract tech background, circuit board style, clean, no text"
      },
      {
        title: "СЕКРЕТ",
        subtitle: "Используйте ИИ-агентов",
        imagePrompt: "futuristic robot holding glowing orb background, neon purple and blue, no text"
      },
      {
        title: "ВЫГОДА",
        subtitle: "Рост продаж на 300%",
        imagePrompt: "upward trending graph glowing neon on dark background, abstract success, no text"
      },
      {
        title: "CTA",
        subtitle: "Сохрани, чтобы не потерять",
        imagePrompt: "dark minimal background with glowing edges, clean, aesthetic, no text"
      }
    ];

    // 2. Генерация фонов (Вызов Vertex AI / GRSai API)
    // Так как нам нужны настоящие ключи, пока что мы ставим красивые фоны из Unsplash / заглушки.
    // Когда вы добавите vertex_sa.json в ENV, здесь будет реальный вызов.
    
    // Эмуляция генерации фонов через ИИ (занимает время)
    await new Promise(r => setTimeout(r, 2000));

    const finalSlides = carouselData.map((slide, index) => ({
      ...slide,
      // Временные эстетичные фоны (до подключения реального API)
      backgroundUrl: `https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&h=1350&fit=crop&auto=format` 
    }));

    return NextResponse.json({ slides: finalSlides });

  } catch (error: any) {
    console.error('Carousel generation error:', error);
    return NextResponse.json({ error: 'Failed to generate carousel' }, { status: 500 });
  }
}
