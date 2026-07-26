# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()
    
    service_account = "vertex_sa.json"
    project_id = "my-project-28666-8-5-26-0-crm"
    location = "us-central1"
    
    if not os.path.exists(service_account):
        print(f"Ошибка: Не найден {service_account}")
        sys.exit(1)
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account
    
    print("Инициализация клиента Vertex AI...")
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    local_video = "04_Design_and_Media/spy_downloads/kaisar_reel.mp4"
    if not os.path.exists(local_video):
        print(f"Ошибка: Файл {local_video} не найден")
        sys.exit(1)
        
    print("Читаем байты kaisar_reel.mp4...")
    with open(local_video, "rb") as f:
        video_bytes = f.read()
        
    print("Формируем запрос к Vertex AI / gemini-2.5-flash...")
    prompt = (
        "Проанализируй оригинальный референсный ролик kaisar_reel.mp4 и найди все B-roll фрагменты (перебивки), "
        "которые не показывают лицо говорящего человека (например, демонстрация телефона, графики, интерфейсов, "
        "процесса работы, скроллинга сайтов и т.д.).\n"
        "Для каждого найденного фрагмента укажи:\n"
        "1. Точные таймкоды начала и конца (в секундах).\n"
        "2. Подробное описание того, что происходит на экране.\n"
        "3. Поясни, к каким словам из нашего нового ролика этот B-roll логически подходит. Наша речь:\n"
        "- 'Хватит платить за дорогие ИИ инструменты.'\n"
        "- 'Эти три сайта позволяют создавать качественный ИИ контент полностью бесплатно.'\n"
        "- 'Первый: Qwen. Он генерирует и изображения, и видео. Да, он немного медленнее, но качество удивительно хорошее.'\n"
        "- 'Второй: Hunyuan. Он с открытым исходным кодом и позволяет создавать кинематографичные визуалы просто из запросов.'\n"
        "- 'Плюс он поддерживает мощные модели типа LX и другие современные видеогенераторы.'\n"
        "- 'И третий: LM арена. Здесь ты можешь сравнивать несколько ИИ моделей бок о бок и мгновенно видеть разные результаты.'\n"
        "- 'Так что вместо угадываний, ты точно знаешь...'\n"
        "- 'Устал сливать бюджеты на подрядчиков? Запусти свой ИИ контент-завод! Пиши слово ВИДЕО в директ, и я скину тебе подробный гайд.'\n"
    )
    
    video_part = types.Part.from_bytes(
        data=video_bytes,
        mime_type="video/mp4"
    )
    
    model_name = "gemini-2.5-flash"
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[video_part, prompt]
        )
        print("\n=== АНАЛИЗ B-ROLL ===")
        print(response.text)
        
        # Сохраняем анализ в файл
        audit_file = "docs/kaisar_brolls_analysis.md"
        with open(audit_file, "w", encoding="utf-8") as f:
            f.write("# Анализ B-roll фрагментов в kaisar_reel.mp4\n\n")
            f.write(response.text)
        print(f"\nОтчет сохранен в {audit_file}")
        
    except Exception as e:
        print(f"Ошибка при запросе к модели: {e}")

if __name__ == "__main__":
    main()
