import os
import sys
import requests
import argparse

def get_grsai_key():
    """Считывает GRSAI_API_KEY из файла .env в корне проекта."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        env_path = ".env"
        
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GRSAI_API_KEY="):
                    return line.strip().split("=")[1].strip()
                    
    return os.environ.get("GRSAI_API_KEY")

def generate_image_grsai(prompt, model_name, output_path, api_key):
    """Генерирует изображение через API GrsAI, используя указанную модель."""
    if not api_key:
        print("Ошибка: GRSAI_API_KEY не найден в файле .env.")
        return False
        
    print(f"Отправка запроса в GrsAI API (Модель: {model_name})...")
    print(f"Промпт: {prompt}")
    
    # GrsAI поддерживает стандартный формат OpenAI Images API
    # Пробуем основной и резервный эндпоинты для стабильности
    endpoints = ["https://api.grsai.com/v1/images/generations", "https://grsai.dakka.com.cn/v1/images/generations"]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1792"  # Вертикальный формат 9:16
    }
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                img_url = result["data"][0]["url"]
                
                # Скачиваем сгенерированное изображение
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"Изображение успешно сохранено в: {output_path}")
                return True
            else:
                print(f"Эндпоинт {url} вернул ошибку {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Не удалось подключиться к {url}: {e}")
            
    print("Ошибка: Не удалось сгенерировать изображение ни через один из эндпоинтов GrsAI.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Генерация кадров через GrsAI API (Nano Banana Pro / Flux).")
    parser.add_argument("--prompt", required=True, help="Промпт для генерации на русском или английском языке.")
    parser.add_argument(
        "--model", 
        default="nano-banana-pro", 
        help="Модель для генерации (nano-banana-pro, nano-banana-2, flux)."
    )
    parser.add_argument("--output", required=True, help="Путь для сохранения готового изображения .png.")
    
    args = parser.parse_args()
    
    api_key = get_grsai_key()
    generate_image_grsai(args.prompt, args.model, args.output, api_key)

if __name__ == "__main__":
    main()
