/**
 * Сервис транскрипции аудио.
 * Приоритет: OpenAI Whisper API → Deepgram → Google Speech-to-Text
 */

interface TranscriptionResult {
  text: string;
  duration?: number;
  provider: string;
}

/**
 * Транскрибирует аудио по URL через OpenAI Whisper API
 */
export async function transcribeWithWhisper(audioUrl: string): Promise<TranscriptionResult> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not set");
  }

  // Скачиваем файл и отправляем в Whisper API
  const audioResponse = await fetch(audioUrl);
  const audioBlob = await audioResponse.blob();

  const formData = new FormData();
  formData.append("file", audioBlob, "audio.ogg");
  formData.append("model", "whisper-1");
  formData.append("language", "ru");
  formData.append("response_format", "json");

  const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Whisper API error: ${response.status} ${errorText}`);
  }

  const data = await response.json();
  return {
    text: data.text,
    provider: "openai-whisper",
  };
}

/**
 * Транскрибирует аудио через Deepgram (альтернатива, дёшево)
 */
export async function transcribeWithDeepgram(audioUrl: string): Promise<TranscriptionResult> {
  const apiKey = process.env.DEEPGRAM_API_KEY;
  if (!apiKey) {
    throw new Error("DEEPGRAM_API_KEY is not set");
  }

  const response = await fetch(
    "https://api.deepgram.com/v1/listen?model=nova-2&language=ru&smart_format=true",
    {
      method: "POST",
      headers: {
        Authorization: `Token ${apiKey}`,
        "Content-Type": "audio/ogg",
      },
      body: await fetch(audioUrl).then((r) => r.blob()),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Deepgram API error: ${response.status} ${errorText}`);
  }

  const data = await response.json();
  const transcript = data.results?.channels?.[0]?.alternatives?.[0]?.transcript || "";

  return {
    text: transcript,
    provider: "deepgram",
  };
}

/**
 * Транскрибирует аудио с автоматическим fallback
 */
export async function transcribeAudio(audioUrl: string): Promise<string> {
  // Пробуем Whisper API
  if (process.env.OPENAI_API_KEY) {
    try {
      const result = await transcribeWithWhisper(audioUrl);
      return result.text;
    } catch (err) {
      console.warn("Whisper API failed, trying Deepgram:", err);
    }
  }

  // Fallback на Deepgram
  if (process.env.DEEPGRAM_API_KEY) {
    try {
      const result = await transcribeWithDeepgram(audioUrl);
      return result.text;
    } catch (err) {
      console.warn("Deepgram also failed:", err);
    }
  }

  throw new Error("No transcription provider available");
}
