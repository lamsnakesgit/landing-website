import asyncio
from celery import Celery
import logging
from agent import run_agent_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app connecting to Redis
app = Celery(
    'ai_orchestrator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Optional configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(name="process_agent_task", bind=True)
def process_agent_task(self, prompt: str, chat_id: int = None):
    """
    Celery task that acts as a bridge to the async Antigravity Agent.
    Celery tasks are synchronous by default, so we wrap the async call.
    """
    logger.info(f"Received task {self.request.id}: prompt='{prompt[:30]}...', chat_id={chat_id}")
    
    try:
        # Run the async agent logic
        result = asyncio.run(run_agent_task(prompt))
        
        # If chat_id is present, we would send a Telegram message back here.
        # e.g., send_telegram_message(chat_id, result)
        if chat_id:
            logger.info(f"Would send result to Telegram chat {chat_id}: {result[:50]}...")
            
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Agent task failed: {e}")
        self.retry(exc=e, countdown=10, max_retries=3)
