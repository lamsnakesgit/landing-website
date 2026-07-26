from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
import httpx
import os
import asyncio

app = FastAPI(title="Carousel & Photo Generator API")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class GenerationRequest(BaseModel):
    request_type: str  # 'carousel' or 'photo'
    prompt: str
    telegram_chat_id: str

# In-memory store to keep track of pending generations waiting for HITL
pending_requests = {}

async def generate_image(model_name: str, prompt: str, chat_id: str):
    """
    Dummy function for actual image generation.
    Here you would call the API for Nano, Ana, or Banana 2, or Contentdrips/Templated.
    """
    # Simulate generation time
    await asyncio.sleep(2)
    message = f"✅ Сгенерировано с помощью модели **{model_name}**!\nПромпт: {prompt}"
    
    # Send result back to Telegram
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        )

@app.post("/api/generate")
async def request_generation(req: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Endpoint called by n8n.
    """
    request_id = str(hash(req.prompt + req.telegram_chat_id))
    pending_requests[request_id] = req
    
    if req.request_type == "carousel":
        # Rule: Nano and Banana 2 strictly for carousels
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Nano", "callback_data": f"gen|{request_id}|Nano"},
                    {"text": "Banana 2", "callback_data": f"gen|{request_id}|Banana 2"}
                ]
            ]
        }
        msg_text = f"🎠 Запрос на карусель.\nВыберите модель (строго Nano или Banana 2):\n\nПромпт: {req.prompt}"
    
    else:
        # Rule: For photos, other models (Vertex, Ana, etc)
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Vertex Imagen", "callback_data": f"gen|{request_id}|Vertex Imagen"},
                    {"text": "Ana", "callback_data": f"gen|{request_id}|Ana"}
                ]
            ]
        }
        msg_text = f"🖼️ Запрос на фото.\nВыберите модель:\n\nПромпт: {req.prompt}"
        
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": req.telegram_chat_id,
                "text": msg_text,
                "reply_markup": keyboard
            }
        )
    
    return {"status": "waiting_for_user", "message": "Отправлен запрос в Telegram для выбора модели."}


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook to receive button clicks from Telegram.
    Set this up by calling: https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>/webhook/telegram
    """
    data = await request.json()
    
    if "callback_query" in data:
        callback_query = data["callback_query"]
        chat_id = callback_query["message"]["chat"]["id"]
        message_id = callback_query["message"]["message_id"]
        callback_data = callback_query["data"]
        
        if callback_data.startswith("gen|"):
            _, req_id, selected_model = callback_data.split("|")
            
            if req_id in pending_requests:
                req = pending_requests.pop(req_id)
                
                # Update message to remove buttons
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{TELEGRAM_API_URL}/editMessageText",
                        json={
                            "chat_id": chat_id,
                            "message_id": message_id,
                            "text": f"⏳ Модель **{selected_model}** выбрана. Идет генерация...",
                            "parse_mode": "Markdown"
                        }
                    )
                
                # Start generation
                background_tasks.add_task(generate_image, selected_model, req.prompt, chat_id)
                
                # Answer callback
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{TELEGRAM_API_URL}/answerCallbackQuery",
                        json={"callback_query_id": callback_query["id"], "text": "Модель принята!"}
                    )
                    
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
