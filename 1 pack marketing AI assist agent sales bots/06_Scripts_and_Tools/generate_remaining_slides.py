import os
import requests
import json

def get_grsai_key():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GRSAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
    return os.environ.get("GRSAI_API_KEY")

def generate_slide(slide_num, prompt, model_name, api_key):
    print(f"Generating Slide {slide_num} with model {model_name}...")
    endpoints = ["https://api.grsai.com/v1/images/generations", "https://grsai.dakka.com.cn/v1/images/generations"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1792"
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
    "", "", "", "",
    "Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay reads: \"OPEN-SOURCE РВЕТ GPT-4\" and a clear text paragraph reads: \"Открытые модели (Llama, DeepSeek) уже нагоняют, а местами и обходят GPT-4. Главное — они бесплатны. Они ставятся на твой личный сервер. Никто не может их забрать или ограничить.\". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\".",
    
    "Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon typography text in the background reads: \"ПИШИ СЛОВО: ОТКРЫТЫЙ\" and a smaller readable text block says: \"Хочешь развернуть свой независимый, нецензурируемый ИИ? Пиши мне в Директ кодовое слово ОТКРЫТЫЙ. Я скину секретную подборку топовых моделей и пошаговую инструкцию по их установке.\". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text \"@lamanopro_ x @aiconicvibe ✔️\"."
]

def main():
    api_key = get_grsai_key()
    if not api_key:
        print("Error: GRSAI_API_KEY not found.")
        return
        
    for i in [5, 6]:
        prompt = prompts[i-1]
        # user said: "grsai api. gpt image 2" -> let's try 'gpt-image-2'
        success = generate_slide(i, prompt, "gpt-image-2", api_key)
        if not success:
            # Let's try standard dall-e-3 just in case grsai proxies it
            print(f"Retrying with dall-e-3 for Slide {i}")
            generate_slide(i, prompt, "dall-e-3", api_key)

if __name__ == "__main__":
    main()
