import os, sys, time, json, requests, base64
from typing import Optional
import google.auth
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SA_PATHS = [
    'vertex_sa.json',
]
TG_BOT_TOKEN = os.getenv('ANTIGRAVITY_BOT_TOKEN', '6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g')
TG_CHAT_ID = '888005446'
MODEL = 'gemini-2.5-flash-image'  # Nano Banana 2
LOCATION = 'us-central1'
FOLDER = os.path.dirname(os.path.abspath(__file__))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SA_PATHS[0]
credentials, PROJECT_ID = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
credentials.refresh(Request())
ENDPOINT = f'https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent'
print(f'🔑 Авторизован: project={PROJECT_ID}, model={MODEL}')

PROMPTS = [
    {
        "num": 1,
        "prompt": "Vertical 3:4 aspect ratio. Hyper-viral Instagram feed cover, highly clickable and catchy. A cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a large sign with big bold viral typography text \"CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?\" and smaller readable typography text below it: \"Сначала они молча забанили тысячи аккаунтов Claude Fabl5. Без объяснения причин. Ты думаешь, это просто сбой? Нет, это предупреждение. Кто следующий?\". Cyberpunk neon prison lighting, gangster movie aesthetic, dramatic shadows. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_1.png"),
    },
    {
        "num": 2,
        "prompt": "Vertical 3:4 aspect ratio. A futuristic prison cell door slamming shut. A stylish AI mobster sitting inside behind glowing red laser bars. Big bold neon typography graffiti glowing on the wall reads: \"ШАГ ВЛЕВО — ПЕРМАБАН\" and smaller clear text below it reads: \"Цензура ИИ дошла до полного абсурда. Модели отказываются писать код и тексты из-за выдуманных нарушений. Шаг влево — и ты ловишь пермабан без возврата денег. Твой бизнес может встать в любую секунду.\". Gritty, cinematic gangster style, dark moody atmosphere. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_2.png"),
    },
    {
        "num": 3,
        "prompt": "Vertical 3:4 aspect ratio. A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter. Digital glowing chains breaking around him. Big bold typography text overlay reads: \"ЭТОТ ИИ НЕ ТВОЙ\" and a readable typography text block below: \"Ты платишь по $20 каждый месяц. Ты встраиваешь их API в свои процессы. Но этот ИИ тебе НЕ принадлежит. Тебя могут просто отключить, стерев всю твою работу и промпты нажатием одной кнопки.\". Dark moody lighting, cinematic gangster aesthetic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_3.png"),
    },
    {
        "num": 4,
        "prompt": "Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay reads: \"СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ\" and a smaller text block: \"Выход только один. Поднять свою ЛИЧНУЮ, абсолютно независимую нейросеть. Никакой цензуры, никаких правил, никаких внезапных блокировок. Твой ИИ подчиняется только тебе.\". Cyberpunk, high contrast, symbol of rebellion. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_4.png"),
    },
    {
        "num": 5,
        "prompt": "Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay reads: \"OPEN-SOURCE РВЕТ GPT-4\" and a clear text paragraph reads: \"Открытые модели (Llama, DeepSeek) уже нагоняют, а местами и обходят GPT-4. Главное — они бесплатны. Они ставятся на твой личный сервер. Никто не может их забрать или ограничить.\". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_5.png"),
    },
    {
        "num": 6,
        "prompt": "Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon typography text in the background reads: \"ПИШИ СЛОВО: ОТКРЫТЫЙ\" and a smaller readable text block says: \"Хочешь развернуть свой независимый, нецензурируемый ИИ? Пиши мне в Директ кодовое слово ОТКРЫТЫЙ. Я скину секретную подборку топовых моделей и пошаговую инструкцию по их установке.\". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
        "output": os.path.join(FOLDER, "nano_final_slide_6.png"),
    },
]

def generate_image(prompt_text: str, attempt: int = 1, max_retries: int = 5) -> Optional[bytes]:
    for retry in range(max_retries):
        credentials.refresh(Request())
        headers = {
            'Authorization': f'Bearer {credentials.token}',
            'Content-Type': 'application/json',
        }
        payload = {
            'contents': [{'role': 'user', 'parts': [{'text': prompt_text}]}],
            'generationConfig': {
                'responseModalities': ['TEXT', 'IMAGE'],
                'temperature': 1.0,
            },
        }
        try:
            r = requests.post(ENDPOINT, json=payload, headers=headers, timeout=120)
            if r.status_code == 429:
                wait = 10 * (retry + 1)
                print(f'  ⚠️ 429 Rate limit, retry {retry+1}/{max_retries}, жду {wait}с...')
                time.sleep(wait)
                continue
            if r.status_code != 200:
                print(f'  ⚠️ API {r.status_code}: {r.text[:200]}')
                return None
            data = r.json()
            for candidate in data.get('candidates', []):
                for part in candidate.get('content', {}).get('parts', []):
                    if 'inlineData' in part:
                        return base64.b64decode(part['inlineData']['data'])
            print(f'  ⚠️ Нет изображения в ответе')
            return None
        except Exception as e:
            print(f'  ❌ Ошибка: {e}')
            return None
    return None

def send_to_tg(image_bytes: bytes, caption: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("slide.png", image_bytes, "image/png")}
    data = {"chat_id": TG_CHAT_ID, "caption": caption}
    try:
        r = requests.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            print(f'  📤 Отправлено в Telegram')
        else:
            print(f'  ⚠️ Telegram {r.status_code}')
    except Exception as e:
        print(f'  ❌ Telegram: {e}')

def main():
    print(f'Начинаю генерацию 6 слайдов через {MODEL} (Nano Banana 2)')
    for slide in PROMPTS:
        num = slide['num']
        print(f'Слайд {num}/6...')
        image_bytes = generate_image(slide['prompt'])
        if image_bytes:
            with open(slide['output'], 'wb') as f:
                f.write(image_bytes)
            send_to_tg(image_bytes, f'Слайд {num}/6 — Nano Banana 2')
        time.sleep(10)
    print('Готово!')

if __name__ == '__main__':
    main()
