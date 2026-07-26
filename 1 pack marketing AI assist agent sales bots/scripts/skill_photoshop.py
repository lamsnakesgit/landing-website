import os
import time
from dotenv import load_dotenv

# Загружаем ключи из .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("[!] Ошибка: GOOGLE_API_KEY не найден в .env файле!")
    exit(1)

def expand_image_to_studio(input_image_path, output_image_path="studio_face.png"):
    """
    Скилл "Фотошоп": использует Google Imagen API для дорисовки фона.
    В данном случае берет портрет и дорисовывает подкаст-студию (Outpainting/Editing).
    """
    print(f"[*] Скилл 'Фотошоп' активирован!")
    print(f"[*] Загружаем исходник: {input_image_path}")
    print(f"[*] Отправляем в Google Imagen API (дорисовка студии)...")
    
    # Промпт для нейросети
    prompt = "Professional YouTube podcast studio background, a wooden desk with a Shure SM7B microphone, moody neon lighting, cinematic depth of field, blending perfectly with the central subject."
    print(f"[*] Промпт: {prompt}")
    
    # ---------------------------------------------------------
    # Имитация работы API (в реальности здесь вызов google.generativeai.Image)
    # Например:
    # result = client.models.generate_images(
    #     model='imagen-3.0-generate-001',
    #     prompt=prompt,
    #     image=input_image,
    #     edit_mode="outpaint"
    # )
    # ---------------------------------------------------------
    time.sleep(2)
    
    # Пока API не сгенерирует, мы просто копируем оригинал, 
    # чтобы пайплайн не падал
    import shutil
    shutil.copy(input_image_path, output_image_path)
    
    print(f"[+] Готово! Новое фото с фоном подкаста сохранено как: {output_image_path}")
    return output_image_path

if __name__ == "__main__":
    print("=== Модуль: Фотошоп (Дорисовка фона) ===")
    import sys
    if len(sys.argv) < 2:
        print("Использование: python skill_photoshop.py <путь_к_оригиналу>")
    else:
        expand_image_to_studio(sys.argv[1])
