import os
import glob
import json
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

_vertex_headers = None
_vertex_url = None

def init_vertex():
    global _vertex_headers, _vertex_url
    if _vertex_headers is not None:
        return True
        
    sa_path = "vertex_sa.json"
    if not os.path.exists(sa_path):
        files = glob.glob("vertex_sa*.json")
        if files:
            sa_path = files[0]
            
    if os.path.exists(sa_path):
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            with open(sa_path, "r") as f:
                sa_info = json.load(f)
                project_id = sa_info.get("project_id")
                
            creds = service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            class CustomRequest(Request):
                def __call__(self, *args, **kwargs):
                    kwargs['timeout'] = 15
                    return super().__call__(*args, **kwargs)
                    
            creds.refresh(CustomRequest())
            location = "us-central1"
            model_name = "gemini-2.5-flash"
            _vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:generateContent"
            _vertex_headers = {
                "Authorization": f"Bearer {creds.token}",
                "Content-Type": "application/json"
            }
            return True
        except Exception as e:
            logger.error(f"KB Outreach Architect: Vertex init error: {e}")
            return False
    return False

def load_knowledge_base():
    """Собирает фрагменты Базы Знаний из 03_Marketing_and_Sales"""
    kb_content = []
    kb_files = [
        "03_Marketing_and_Sales/business_sales_strategy.md",
        "03_Marketing_and_Sales/ai_agent_funnel.md",
        "03_Marketing_and_Sales/lead_magnet_architect.md"
    ]
    for filepath in kb_files:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    kb_content.append(f"--- SOURCE: {os.path.basename(filepath)} ---\n" + f.read()[:2000])
            except Exception:
                pass
    return "\n\n".join(kb_content)

def generate_outreach_sequence(lead_data):
    """
    Генерирует 4-шаговую цепочку автоворонки для квалифицированного лида на базе знаний
    с адаптацией под источник (Threads, Twitter/X, LinkedIn, Telegram, WhatsApp, Email).
    """
    init_vertex()
    kb_snippets = load_knowledge_base()
    source = lead_data.get('source', 'WhatsApp / Telegram')
    
    system_prompt = (
        f"Вы — топовый B2B Sales Architect. Создайте 4-шаговую цепочку персональных сообщений "
        f"для источника '{source}' на основе материалов Базы Знаний.\n\n"
        "ПРАВИЛА НАПИСАНИЯ ПО КАНАЛАМ:\n"
        "- Threads / X (Twitter): Короткие лаконичные DM сообщения (до 280 символов), очень дружелюбно, без форматирования.\n"
        "- LinkedIn: Профессиональный тон B2B ЛПР, фокус на ROI, автоматизацию процессов и кейсы.\n"
        "- Telegram / WhatsApp: Естественный диалоговый стиль, разбивка на короткие абзацы.\n\n"
        "ПРАВИЛА ШАГОВ:\n"
        "1. Шаг 1 (День 1): Персональный хук, признание специфики компании/поста, вопрос про боли.\n"
        "2. Шаг 2 (День 2): Ценностный кейс из Базы Знаний (увеличение конверсии в 2-3 раза).\n"
        "3. Шаг 3 (День 4): Предложение интерактивного демо (бесплатный прототип бота за 1 день).\n"
        "4. Шаг 4 (День 7): Легкий CTA / Завершающий вопрос без давления.\n\n"
        "Верните результат СТРОГО в JSON:\n"
        "{\n"
        '  "company_name": "...",\n'
        '  "target_channel": "...",\n'
        '  "sequence": [\n'
        '    {"step": 1, "delay_days": 0, "title": "Первичный контакт", "text": "..."},\n'
        '    {"step": 2, "delay_days": 1, "title": "Кейс и социальное доказательство", "text": "..."},\n'
        '    {"step": 3, "delay_days": 3, "title": "Интерактивное демо", "text": "..."},\n'
        '    {"step": 4, "delay_days": 6, "title": "Софт CTA / Завершение", "text": "..."}\n'
        '  ]\n'
        "}"
    )
    
    user_prompt = (
        f"Данные квалифицированного лида:\n"
        f"Компания / Ник: {lead_data.get('company_name')}\n"
        f"Контакт: {lead_data.get('name')}\n"
        f"Источник: {source}\n"
        f"Телефон/Соцсеть: {lead_data.get('phone') or lead_data.get('telegram') or lead_data.get('profile_url')}\n"
        f"Запрос / Ниша: {lead_data.get('query')}\n"
        f"Сниппет / Боль: {lead_data.get('snippet', lead_data.get('pain_hypothesis', 'Нехватка автоворонок'))}\n\n"
        f"База Знаний (Кейсы и Материалы):\n{kb_snippets[:3000]}\n"
    )
    
    if _vertex_headers and _vertex_url:
        try:
            body = {
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(_vertex_url, json=body, headers=_vertex_headers, timeout=25)
            if res.status_code == 200:
                res_json = res.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                clean_text = text.strip().removeprefix("```json").removesuffix("```").strip()
                return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Ошибка вызова Gemini в kb_outreach_architect: {e}")
            
    # Запасной дефолтный шаблон цепочки
    return {
        "company_name": lead_data.get('company_name'),
        "target_channel": source,
        "sequence": [
            {"step": 1, "delay_days": 0, "title": "Первичный контакт", "text": f"Привет! Увидел ваш запрос по '{lead_data.get('query', 'автоматизации')}'. Вы сейчас используете ИИ для обработки клиентов?"},
            {"step": 2, "delay_days": 1, "title": "Кейс и соц. доказательство", "text": "Кстати, наш кейс: навели порядок в воронке через n8n и подняли конверсию лидов на 35%. Хотите скину короткий разбор?"},
            {"step": 3, "delay_days": 3, "title": "Интерактивное демо", "text": "Мы можем собрать тест-бота под ваш запрос за 1 день. Интересно протестировать?"},
            {"step": 4, "delay_days": 6, "title": "Софт CTA", "text": "Если вопрос автоматизации пока не актуален — дайте знать, не буду отвлекать. Удачного дня!"}
        ]
    }

if __name__ == "__main__":
    sample_lead = {
        "company_name": "@threads_founder",
        "name": "Данияр",
        "source": "Threads.net",
        "query": "нужен ИИ маркетолог",
        "snippet": "Ищу разработчика или агентство для настройки ИИ-ассистента"
    }
    result = generate_outreach_sequence(sample_lead)
    print("\n--- Сгенерированная 4-шаговая цепочка под Threads ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))
