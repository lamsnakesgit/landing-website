from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from tasks import process_agent_task
import uuid

app = FastAPI(title="AI Orchestrator Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    prompt: str
    chat_id: Optional[int] = None
    priority: str = "normal"

# In-memory store for demo Kanban purposes (Production should use DB/Redis)
task_store = []



@app.post("/tasks")
def create_task(req: TaskRequest):
    # Generate ID and send task to Celery Queue
    task_id = str(uuid.uuid4())
    task = process_agent_task.apply_async(args=[req.prompt, req.chat_id], task_id=task_id)
    
    task_record = {
        "id": task_id,
        "prompt": req.prompt,
        "status": "queued",
        "chat_id": req.chat_id
    }
    task_store.append(task_record)
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/tasks/all")
def get_all_tasks():
    # In a real app, query Celery backend/Redis or a database
    # For the mock Kanban, we return the in-memory store.
    # We can also check task.state if we want, but for now we just return the list.
    return {"tasks": task_store}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Webhook endpoint for Telegram Bot.
    """
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if text and chat_id:
        task_id = str(uuid.uuid4())
        process_agent_task.apply_async(args=[text, chat_id], task_id=task_id)
        task_store.append({
            "id": task_id,
            "prompt": text,
            "status": "queued",
            "chat_id": chat_id
        })
        
    return {"ok": True}

# Mount frontend as static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
