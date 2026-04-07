from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import edge_tts
import io
import asyncio

app = FastAPI(title="Edge TTS API")

class TTSRequest(BaseModel):
    text: str
    voice: str = "ru-RU-SvetlanaNeural"
    rate: str = "-5%"   # скорость: -10% медленнее, +10% быстрее
    volume: str = "+0%" # громкость

@app.get("/")
def health():
    return {"status": "ok", "service": "edge-tts"}

@app.get("/voices")
async def list_voices():
    voices = await edge_tts.list_voices()
    ru_voices = [v for v in voices if v["Locale"].startswith("ru-")]
    return {"voices": ru_voices}

@app.post("/tts")
async def synthesize(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Текст пустой")

    try:
        communicate = edge_tts.Communicate(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            volume=req.volume
        )

        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_buffer.seek(0)

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=tts.mp3"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
