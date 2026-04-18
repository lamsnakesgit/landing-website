import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(".env")
api_key = os.environ.get("GOOGLE_API_KEY")

def analyze_video_for_veo(video_path):
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    
    print(f"Uploading video: {video_path}...")
    video_file = client.files.upload(file=video_path)
    print(f"Completed upload: {video_file.uri}")

    # Wait for the file to be processed
    while video_file.state.name == "PROCESSING":
        print("Processing video...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed: {video_file.state.name}")

    print("Video processed. Analyzing...")

    prompt_text = """
    Задача: Проанализируй прикрепленное видео и создай детальный технический сценарий для воссоздания 1 в 1 в Google Veo 3.1 Light.
    
    Инструкции:
    1. Визуальный стиль: Опиши общую эстетику (освещение, цветовая палитра, движение камеры, тип линзы).
    2. Разбор по сценам: Для каждой сцены/склейки укажи:
        - Таймкод: Начало и конец.
        - Визуальное описание: Что именно происходит (объект, действие, фон).
        - Работа камеры: (например, "Медленный зум", "Панорама влево", "Статичный крупный план").
        - Текст на экране: Любой текст, его стиль и позиция.
    3. Промпты для Google Veo 3.1 Light: Создай 3-5 специфичных промптов на АНГЛИЙСКОМ языке, используя формулу:
       [Subject] + [Action] + [Environment] + [Lighting] + [Camera Movement] + [Style/Lens]
       
       Добавляй технические детали: "4k resolution", "highly detailed textures", "cinematic lighting", "shot on iPhone 15 Pro" (если подходит по стилю).
    
    Формат вывода:
    - Резюме стиля
    - Таблица сцен
    - Кинематографичные промпты для Google Veo (на английском)
    """

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    types.Part.from_text(text=prompt_text)
                ]
            )
        ]
    )

    print("\n--- ANALYSIS RESULT ---\n")
    print(response.text)
    
    with open("docs/video_analysis_results.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\nAnalysis saved to docs/video_analysis_results.md")

if __name__ == "__main__":
    video_path = "assets/IMG_1400_sen sulu_beauty_.MP4"
    analyze_video_for_veo(video_path)
