import os
import requests
import json
import time

def get_grsai_key():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GRSAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
    return os.environ.get("GRSAI_API_KEY")

def generate_carousel_slide(slide_num, prompt, model_name, api_key):
    print(f"Generating Slide {slide_num}...")
    endpoints = ["https://api.grsai.com/v1/images/generations", "https://grsai.dakka.com.cn/v1/images/generations"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 3:4 format usually is 768x1024
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n": 1,
        "size": "768x1024"
    }
    
    output_path = f"carousel_slide_{slide_num}.png"
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                img_url = result["data"][0]["url"]
                
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"Successfully saved {output_path}")
                return True
            else:
                print(f"Endpoint {url} returned error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")
            
    return False

prompts = [
    "Vertical 3:4 aspect ratio. Hyper-viral Instagram feed cover, highly clickable and catchy. A cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a large sign with big bold viral typography text \"CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?\" and smaller readable typography text below it: \"Сначала они молча забанили тысячи аккаунтов Claude Fabl5. Без объяснения причин. Ты думаешь, это просто сбой? Нет, это предупреждение. Кто следующий?\". Cyberpunk neon prison lighting, gangster movie aesthetic, dramatic shadows. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A futuristic prison cell door slamming shut. A stylish AI mobster sitting inside behind glowing red laser bars. Big bold neon typography graffiti glowing on the wall reads: \"ШАГ ВЛЕВО — ПЕРМАБАН\" and smaller typography text below: \"Любое подозрительное действие — бан без права апелляции. Они создали самую умную нейросеть, а потом посадили ее на цепь. Выживут только те, кто знает правила игры.\". Gritty, cinematic gangster style, dark moody atmosphere. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter. Digital glowing chains breaking around him. Big bold typography text overlay reads: \"ЭТОТ ИИ НЕ ТВОЙ\" and a readable typography text: \"Ты платишь 20 баксов в месяц, но ИИ тебе не принадлежит. Одно неверное слово — и твой аккаунт стерт. Данные уничтожены. Бизнес встал. Пора менять правила.\". Dark moody lighting, cinematic gangster aesthetic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold glowing typography text overlay: \"СВОБОДА ИЛИ БАН?\" and smaller typography text: \"Выбор за тобой. Либо ты продолжаешь трястись над каждым промптом, либо строишь свою независимую нейро-империю. Локальные модели, обход ограничений, свобода.\". Cyberpunk, high contrast, symbol of rebellion. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay reads: \"СИНДИКАТ\" and smaller typography text: \"Мы знаем, как обойти систему. Мы используем обходные пути, свои сервера и независимые нейросети. Хочешь быть с нами или останешься в цифровой клетке?\". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold typography text overlay: \"КЛЮЧ К СВОБОДЕ\" and smaller typography text: \"В моем Telegram-канале я выложил полную схему обхода банов и список свободных нейросетей, которые не закроют твой бизнес. Ссылка в описании.\". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\"."
]

def main():
    api_key = get_grsai_key()
    if not api_key:
        print("Error: GRSAI_API_KEY not found.")
        return
        
    model = "nano-banana-2"
    
    for i, prompt in enumerate(prompts, 1):
        success = generate_carousel_slide(i, prompt, model, api_key)
        if not success:
            print(f"Retrying with nano-banana-pro for Slide {i}")
            generate_carousel_slide(i, prompt, "nano-banana-pro", api_key)
        time.sleep(2)

if __name__ == "__main__":
    main()
