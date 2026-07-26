import os
import requests
import time

def get_grsai_key():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GRSAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
    return os.environ.get("GRSAI_API_KEY")

TG_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN", "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g")
TG_CHAT_ID = "888005446"

def send_to_tg(image_bytes: bytes, caption: str) -> bool:
    """Отправка фото в Telegram."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("slide.png", image_bytes, "image/png")}
    data = {"chat_id": TG_CHAT_ID, "caption": caption}
    try:
        r = requests.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            print(f"    📤 Отправлено в Telegram")
            return True
        else:
            print(f"    ❌ Telegram {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"    ❌ Telegram ошибка: {e}")
    return False

def generate_carousel_slide(slide_num, prompt, model_name, api_key):
    print(f"Generating Slide {slide_num}...")
    endpoints = ["https://api.grsai.com/v1/images/generations", "https://grsai.dakka.com.cn/v1/images/generations"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n": 1,
        "size": "768x1024"
    }
    
    output_path = f"carousel_slide_{slide_num}.png"
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                result = response.json()
                img_url = result["data"][0]["url"]
                
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"Successfully saved {output_path}")
                send_to_tg(img_data, "2 22")
                return True
            else:
                print(f"Endpoint {url} returned error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")
            
    return False

prompts = [
    "Vertical 3:4 aspect ratio. Hyper-viral Instagram feed cover, highly clickable and catchy. A cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a large sign with big bold viral typography text \"CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?\" and smaller readable typography text below it: \"Сначала они молча забанили тысячи аккаунтов Claude Fabl5. Без объяснения причин. Ты думаешь, это просто сбой? Нет, это предупреждение. Кто следующий?\". Cyberpunk neon prison lighting, gangster movie aesthetic, dramatic shadows. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A futuristic prison cell door slamming shut. A stylish AI mobster sitting inside behind glowing red laser bars. Big bold neon typography graffiti glowing on the wall reads: \"ШАГ ВЛЕВО — ПЕРМАБАН\" and smaller clear text below it reads: \"Цензура ИИ дошла до полного абсурда. Модели отказываются писать код и тексты из-за выдуманных нарушений. Шаг влево — и ты ловишь пермабан без возврата денег. Твой бизнес может встать в любую секунду.\". Gritty, cinematic gangster style, dark moody atmosphere. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter. Digital glowing chains breaking around him. Big bold typography text overlay reads: \"ЭТОТ ИИ НЕ ТВОЙ\" and a readable typography text block below: \"Ты платишь по $20 каждый месяц. Ты встраиваешь их API в свои процессы. Но этот ИИ тебе НЕ принадлежит. Тебя могут просто отключить, стерев всю твою работу и промпты нажатием одной кнопки.\". Dark moody lighting, cinematic gangster aesthetic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay reads: \"СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ\" and a smaller text block: \"Выход только один. Поднять свою ЛИЧНУЮ, абсолютно независимую нейросеть. Никакой цензуры, никаких правил, никаких внезапных блокировок. Твой ИИ подчиняется только тебе.\". Cyberpunk, high contrast, symbol of rebellion. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay reads: \"OPEN-SOURCE РВЕТ GPT-4\" and a clear text paragraph reads: \"Открытые модели (Llama, DeepSeek) уже нагоняют, а местами и обходят GPT-4. Главное — они бесплатны. Они ставятся на твой личный сервер. Никто не может их забрать или ограничить.\". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon typography text in the background reads: \"ПИШИ СЛОВО: ОТКРЫТЫЙ\" and a smaller readable text block says: \"Хочешь развернуть свой независимый, нецензурируемый ИИ? Пиши мне в Директ кодовое слово ОТКРЫТЫЙ. Я скину секретную подборку топовых моделей и пошаговую инструкцию по их установке.\". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\"."
]

def main():
    api_key = get_grsai_key()
    if not api_key:
        print("Error: GRSAI_API_KEY not found.")
        return
        
    model = "nano-banana-pro"
    
    for i, prompt in enumerate(prompts, 1):
        success = generate_carousel_slide(i, prompt, model, api_key)
        if not success:
            print(f"Retrying with nano-banana-2 for Slide {i}")
            generate_carousel_slide(i, prompt, "nano-banana-2", api_key)
        time.sleep(2)

if __name__ == "__main__":
    main()
