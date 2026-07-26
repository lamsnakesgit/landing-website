# -*- coding: utf-8 -*-
import os
import sys
import time
import glob
from dotenv import load_dotenv
from google import genai

def main():
    # Загружаем переменные окружения из .env
    load_dotenv()
    
    # Получаем API ключ
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Ошибка: GOOGLE_API_KEY не найден в файле .env")
        sys.exit(1)
        
    # Инициализируем клиент Google GenAI
    client = genai.Client(api_key=api_key)
    
    # Находим файл видеоролика референса
    search_path = "2 1 контент план_/референс донор контент видео/claude_gpt_competitor_*.mp4"
    matching_files = glob.glob(search_path)
    
    if not matching_files:
        print(f"Ошибка: Не найден файл по шаблону {search_path}")
        sys.exit(1)
        
    video_path = matching_files[0]
    print(f"Найден файл для анализа: {video_path}")
    
    print("Загружаем видео в Gemini File API...")
    video_file = client.files.upload(file=video_path)
    print(f"Файл загружен. Имя на сервере: {video_file.name}")
    
    # Ожидаем завершения обработки видео
    try:
        while True:
            video_file = client.files.get(name=video_file.name)
            state = video_file.state.name
            print(f"Текущее состояние обработки видео: {state}")
            if state == "ACTIVE":
                print("Видео готово к анализу!")
                break
            elif state == "FAILED":
                print(f"Ошибка обработки видео: {video_file.error.message}")
                sys.exit(1)
            time.sleep(10)
            
        print("Шаг 1: Извлекаем транскрипцию и анализируем структуру видео...")
        prompt_analysis = (
            "Проанализируй это видео. Выполни следующие задачи:\n"
            "1. Сделай полную дословную транскрипцию того, что говорится в видео (на языке оригинала, но если есть английский — переведи основные мысли на русский язык).\n"
            "2. Опиши структуру видео: какой хук (зацепка) используется, каков темп, какие визуальные переходы/кадры присутствуют, в чем главная ценность контента.\n"
            "Ответь на русском языке."
        )
        
        response_analysis = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt_analysis]
        )
        analysis_text = response_analysis.text
        print("Анализ структуры успешно завершен.")
        
        print("Шаг 2: Генерируем уникальные вирусные сценарии...")
        prompt_rewrite = (
            f"На основе структуры и транскрипта этого видео: \n\n{analysis_text}\n\n"
            "Создай 3 уникальных варианта сценария для вертикального видео (Reels/Shorts/TikTok) на русском языке.\n"
            "Каждый вариант должен отвечать следующим требованиям:\n"
            "1. Сохранять сильный хук (зацепку) в первые 3 секунды.\n"
            "2. Быть адаптированным для эксперта по ИИ-автоматизации и ИИ-агентам.\n"
            "3. Логично подводить к призыву к действию (CTA): 'Забери пак промптов и гайд по сервисам и напиши 'ПАК' в лс' (или вариации этого призыва, органично встроенные в финал).\n"
            "4. Включать пометки для визуала (что показывать на экране) и темпа речи.\n\n"
            "Варианты должны отличаться стилем подачи:\n"
            "- Вариант 1: Быстрый динамичный Reels в стиле Алекса Хормози (акцент на боли, цифры, резкие тезисы).\n"
            "- Вариант 2: Экспертный разбор (акцент на пользу, пошаговый алгоритм, демонстрация экрана).\n"
            "- Вариант 3: Креативный/Интригующий (через необычную аналогию или сторителлинг)."
        )
        
        response_rewrite = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt_rewrite]
        )
        rewrite_text = response_rewrite.text
        print("Генерация новых сценариев завершена.")
        
        # Записываем результаты в файл
        output_file_path = "2 1 контент план_/claude_gpt_competitor_rewritten.md"
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("# Результаты анализа и уникализации видео\n\n")
            f.write("## Исходный транскрипт и анализ структуры референса\n\n")
            f.write(analysis_text)
            f.write("\n\n---\n\n")
            f.write("## Уникальные варианты сценариев (Reels / Shorts)\n\n")
            f.write(rewrite_text)
            
        print(f"Все результаты успешно сохранены в файл: {output_file_path}")
        
    finally:
        # Очищаем загруженный файл на стороне Gemini
        print("Удаляем временный видеофайл с серверов Gemini...")
        client.files.delete(name=video_file.name)
        print("Временный файл удален.")

if __name__ == "__main__":
    main()
