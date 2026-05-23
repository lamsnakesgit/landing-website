import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

from smm_brand_ai.planner.prompts import CREATIVE_ANALYZER_PROMPT

load_dotenv()

class CreativeAnalyzer:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.rag_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "reference_rag"
        )
        os.makedirs(self.rag_dir, exist_ok=True)
        
        # Клиент OpenAI
        self.client = None
        if self.openai_key:
            clean_key = self.openai_key.strip().rstrip('.')
            self.client = OpenAI(api_key=clean_key)

    def analyze_reference(self, reference_text: str, our_script: str, reference_metadata: dict = None) -> str:
        """
        Сравнивает референс с нашим сценарием и выдает ИИ-анализ и оптимизированный сценарий.
        """
        if not self.client:
            logger.error("[ANALYZER] OpenAI клиент не настроен!")
            return "Ошибка: не настроен OPENAI_API_KEY."

        if not reference_metadata:
            reference_metadata = {}

        logger.info("[ANALYZER] Запуск сравнительного анализа с референсом...")
        
        prompt_user = (
            f"=== УСПЕШНЫЙ ВИДЕО-РЕФЕРЕНС ===\n"
            f"Метаданные: {json.dumps(reference_metadata, ensure_ascii=False)}\n"
            f"Текст/Транскрипт референса:\n{reference_text}\n\n"
            f"=== НАШ ПРЕДЛАГАЕМЫЙ СЦЕНАРИЙ ===\n"
            f"{our_script}\n\n"
            f"Проведи глубокий сравнительный анализ и напиши улучшенный сценарий."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Используем gpt-4o-mini для скорости и экономии, либо gpt-4o для тяжелого reasoning
                messages=[
                    {"role": "system", "content": CREATIVE_ANALYZER_PROMPT},
                    {"role": "user", "content": prompt_user}
                ],
                temperature=0.7,
                timeout=90
            )

            analysis_result = response.choices[0].message.content
            
            # Сохраняем анализ в RAG-папку для накопления базы знаний
            ref_name = reference_metadata.get("title") or f"ref_{datetime.now().strftime('%H%M%S')}"
            # Очищаем имя от запрещенных символов для файловой системы
            safe_ref_name = "".join(c for c in ref_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            safe_ref_name = safe_ref_name.replace(" ", "_")[:50]
            
            file_name = f"analysis_{datetime.now().strftime('%Y%m%d')}_{safe_ref_name}.md"
            file_path = os.path.join(self.rag_dir, file_name)
            
            # Структурируем markdown файл для RAG
            rag_content = (
                f"# Анализ креатива: {ref_name}\n"
                f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Платформа: {reference_metadata.get('platform', 'Не указана')}\n"
                f"Просмотры референса: {reference_metadata.get('views', 'Неизвестно')}\n\n"
                f"## Исходный референс:\n```\n{reference_text}\n```\n\n"
                f"## Наш старый сценарий:\n```\n{our_script}\n```\n\n"
                f"## ИИ-Анализ и рекомендации:\n\n{analysis_result}\n"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(rag_content)

            logger.info(f"[ANALYZER] Отчет об анализе креатива сохранен в {os.path.basename(file_path)}")
            return analysis_result

        except Exception as e:
            logger.error(f"[ANALYZER] Ошибка анализа креатива: {str(e)}")
            return f"Ошибка при анализе креатива: {str(e)}"
            
if __name__ == "__main__":
    # Тестовый запуск
    analyzer = CreativeAnalyzer()
    
    test_ref = "Как зарабатывать 500к в месяц на ИИ-ботах. Показываю схему. Сначала делаем лид-магнит. Потом настраиваем рассылку. И закрываем клиентов в Telegram. Ссылка на бота в профиле!"
    test_our = "Здравствуйте. Мы делаем ИИ-ботов для бизнеса. Это помогает автоматизировать продажи и экономить время. Напишите нам, чтобы заказать внедрение."
    
    meta = {"title": "Бот за 500к схема", "platform": "reels", "views": 150000}
    
    res = analyzer.analyze_reference(test_ref, test_our, meta)
    print("\n--- РЕЗУЛЬТАТ АНАЛИЗА КРЕАТИВА ---")
    print(res)
