import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
import google.auth
from google.auth.transport.requests import Request
from google import genai
from google.genai import types

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='skills_api.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="n8n Skills API (with HITL)", description="API обертка для ИИ-навыков с поддержкой Human-in-the-Loop")

# -- Конфигурация --
VERTEX_SA_PATH = "vertex_sa.json"
PROJECT_ID = "my-project-28666-8-5-26-0-crm"
LOCATION = "us-central1"

if os.path.exists(VERTEX_SA_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = VERTEX_SA_PATH
else:
    logger.warning("Файл vertex_sa.json не найден!")

try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logger.error(f"Ошибка инициализации клиента GenAI: {e}")
    client = None

# --- Pydantic Модели ---
class PromptEnhanceRequest(BaseModel):
    task_type: str # "image", "video", "carousel"
    raw_prompt: str
    feedback: Optional[str] = None # Заполняется, если юзер в ТГ попросил "докрутить"

class ImageExecuteRequest(BaseModel):
    final_prompt: str
    aspect_ratio: str = "1:1"
    fallback: bool = True

class VideoExecuteRequest(BaseModel):
    final_prompt: str
    image_path: Optional[str] = None

class OfferRequest(BaseModel):
    target_audience: str
    niche: str
    offer_type: str

class JobResponseRequest(BaseModel):
    job_description: str
    my_resume: str

class SalesConsultantRequest(BaseModel):
    client_message: str
    funnel_stage: str
    history: Optional[str] = ""

# --- HITL: ЭТАП 1 (Генерация / Докрутка Промпта) ---
@app.post("/api/skills/enhance-prompt")
async def enhance_prompt(req: PromptEnhanceRequest):
    """
    Генерирует или улучшает промпт для видео/картинок/каруселей с учетом правок (feedback) от юзера.
    Это первый шаг в n8n перед вызовом реальной генерации (HITL).
    """
    logger.info(f"Enhance prompt for {req.task_type}")
    
    if req.task_type == "video":
        sys_instr = "Ты топовый видео-режиссер и спец по нейросетям. Преврати простую идею пользователя в идеальный, детальный промпт на английском языке для генератора видео Vertex Veo 3.1. Опиши свет, движение камеры, текстуры, качество (cinematic, 4k, slow motion). Если юзер дает 'Правки', измени промпт с их учетом."
    elif req.task_type == "image":
        sys_instr = "Ты профессиональный ИИ-художник. Преврати идею в мощный промпт на английском языке для генератора картинок (Midjourney/Imagen). Укажи стиль, освещение, детали, перспективу. Если есть 'Правки', учти их."
    elif req.task_type == "carousel":
        sys_instr = "Ты топовый инста-маркетолог. Создай черновик вирусной карусели на 5-7 слайдов. Для каждого слайда дай: 1. Текст на самом слайде (коротко и емко) 2. Промпт для генерации картинки к этому слайду 3. Текст для поста. Учти правки, если они есть."
    else:
        raise HTTPException(status_code=400, detail="Invalid task_type. Must be image, video, or carousel.")
        
    prompt = f"Исходная идея: {req.raw_prompt}"
    if req.feedback:
        prompt += f"\n\nПравки от клиента (докрути с учетом этого): {req.feedback}"
        
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=sys_instr, temperature=0.7)
        )
        return {"status": "success", "enhanced_prompt": response.text}
    except Exception as e:
        logger.error(f"Enhance prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- HITL: ЭТАП 2 (Выполнение Генерации) ---
@app.post("/api/skills/execute-image")
async def execute_image(req: ImageExecuteRequest):
    """Генерация картинки по финальному (одобренному юзером) промпту"""
    logger.info(f"Execute Image: {req.final_prompt}")
    try:
        credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(Request())
        
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{project}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
        headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json; charset=utf-8"}
        data = {
            "instances": [{"prompt": req.final_prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": req.aspect_ratio}
        }
        
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            res_json = resp.json()
            if 'predictions' in res_json and len(res_json['predictions']) > 0:
                img_b64 = res_json['predictions'][0].get('bytesBase64Encoded')
                if img_b64:
                    return {"status": "success", "image_base64": img_b64}
                    
        if req.fallback:
            return {"status": "fallback_used", "message": "Фоллбек (напишите логику aihubmix)", "prompt": req.final_prompt}
            
        raise HTTPException(status_code=500, detail=f"Imagen error: {resp.text}")
    except Exception as e:
        logger.error(f"Image execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/execute-video")
async def execute_video(req: VideoExecuteRequest, background_tasks: BackgroundTasks):
    """Генерация видео Veo по финальному промпту"""
    logger.info(f"Execute Video: {req.final_prompt}")
    
    def run_veo_job(prompt, img_path):
        try:
            config_args = {}
            if img_path and os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                img = types.Image(image_bytes=img_bytes, mime_type="image/png")
                ref_image = types.VideoGenerationReferenceImage(image=img, reference_type="ASSET")
                config_args['referenceImages'] = [ref_image]
                
            response = client.models.generate_videos(
                model='veo-3.1-generate-001',
                prompt=prompt,
                config=types.GenerateVideosConfig(**config_args)
            )
            logger.info(f"Veo job started: {response}")
            # TODO: Add webhook to n8n when operation is done
        except Exception as e:
            logger.error(f"Veo error: {e}")

    background_tasks.add_task(run_veo_job, req.final_prompt, req.image_path)
    return {"status": "processing", "message": "Veo задача поставлена в очередь (~10 минут)."}

# --- ОСТАЛЬНЫЕ НАВЫКИ ---
@app.post("/api/skills/write-offer")
async def write_offer(req: OfferRequest):
    sys_instr = "Ты крутой маркетолог. Пиши заголовки по 4U, боли и мощные CTA для лендингов/креативов."
    prompt = f"ЦА: {req.target_audience}\nНиша: {req.niche}\nТип: {req.offer_type}"
    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt, config=types.GenerateContentConfig(system_instruction=sys_instr, temperature=0.8))
        return {"status": "success", "offer_text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/write-job-response")
async def write_job_response(req: JobResponseRequest):
    sys_instr = "Ты эксперт по найму. Пиши отклики с позиции сильного партнера, акцент на прибыль бизнеса."
    prompt = f"Вакансия:\n{req.job_description}\n\nРезюме:\n{req.my_resume}"
    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt, config=types.GenerateContentConfig(system_instruction=sys_instr, temperature=0.7))
        return {"status": "success", "response_text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/sales-consultant")
async def sales_consultant(req: SalesConsultantRequest):
    sys_instr = "Ты гениальный продавец (микс Дашкиева, Гребенюка, Хормози). Квалифицируй, амортизируй возражения ('Да, я понимаю...'), веди воронку."
    prompt = f"История:\n{req.history}\n\nЭтап воронки: {req.funnel_stage}\nКлиент пишет: {req.client_message}\n\nНапиши ответ и краткий анализ."
    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt, config=types.GenerateContentConfig(system_instruction=sys_instr, temperature=0.5))
        return {"status": "success", "sales_reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
