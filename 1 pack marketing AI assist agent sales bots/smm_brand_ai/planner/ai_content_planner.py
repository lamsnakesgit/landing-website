import os
import json
from datetime import datetime
import requests
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

from smm_brand_ai.planner.prompts import PLANNER_SYSTEM_PROMPT

load_dotenv()

class AIContentPlanner:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        # Локальный fallback
        self.local_db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "database", 
            "local_smm_data.json"
        )
        
        # Создаем папку для готовых планов
        self.plans_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "generated_plans"
        )
        os.makedirs(self.plans_dir, exist_ok=True)

        # Клиент OpenAI
        self.client = None
        if self.openai_key:
            clean_key = self.openai_key.strip().rstrip('.')
            self.client = OpenAI(api_key=clean_key)

    def get_best_performing_content(self, limit: int = 10) -> str:
        """
        Извлекает топ лучших постов по ER и просмотрам за последний месяц.
        Пробует Supabase, при отсутствии данных переключается на локальный JSON.
        """
        posts_data = []

        if self.supabase_url and self.supabase_key:
            # Делаем запрос к Supabase, объединяя посты и метрики через REST API
            # Извлекаем данные за последние 30 дней, сортируем по ER
            url = f"{self.supabase_url.rstrip('/')}/rest/v1/smm_metrics_history"
            params = {
                "select": "platform,post_id,views,likes,comments,shares,er,tracked_date,smm_posts(title,url)",
                "order": "er.desc",
                "limit": str(limit)
            }
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
            try:
                res = requests.get(url, headers=headers, params=params, timeout=10)
                if res.status_code == 200:
                    raw_data = res.json()
                    for item in raw_data:
                        post_info = item.get("smm_posts", {})
                        title = post_info.get("title", "Без названия") if post_info else "Без названия"
                        url_post = post_info.get("url", "") if post_info else ""
                        
                        posts_data.append({
                            "platform": item["platform"],
                            "title": title,
                            "url": url_post,
                            "views": item["views"],
                            "likes": item["likes"],
                            "comments": item["comments"],
                            "er": item["er"],
                            "date": item["tracked_date"]
                        })
            except Exception as e:
                logger.error(f"[PLANNER] Ошибка запроса к Supabase: {str(e)}")

        # Fallback на локальный JSON
        if not posts_data and os.path.exists(self.local_db_path):
            logger.info("[PLANNER] Supabase пуст или недоступен. Загрузка лучших постов из локальной базы...")
            try:
                with open(self.local_db_path, "r", encoding="utf-8") as f:
                    local_db = json.load(f)
                    metrics = local_db.get("metrics", {})
                    posts = local_db.get("posts", {})
                    
                    # Сортируем локальные метрики по ER
                    sorted_metrics = sorted(
                        metrics.values(), 
                        key=lambda x: x.get("er", 0.0), 
                        reverse=True
                    )
                    
                    for m in sorted_metrics[:limit]:
                        post_key = f"{m['platform']}_{m['post_id']}"
                        p_info = posts.get(post_key, {})
                        posts_data.append({
                            "platform": m["platform"],
                            "title": p_info.get("title", "Без названия"),
                            "url": p_info.get("url", ""),
                            "views": m["views"],
                            "likes": m["likes"],
                            "comments": m["comments"],
                            "er": m["er"],
                            "date": m["tracked_date"]
                        })
            except Exception as e:
                logger.error(f"[PLANNER] Ошибка чтения локального JSON: {str(e)}")

        # Форматируем данные в виде текста для промпта
        if not posts_data:
            return "Нет исторических данных по контенту. Сгенерируйте базовый контент-план с нуля."

        summary_text = "Топ постов по вовлеченности за прошлый период:\n"
        for i, p in enumerate(posts_data, 1):
            summary_text += (
                f"{i}. [{p['platform'].upper()}] '{p['title']}'\n"
                f"   Просмотры: {p['views']} | Лайки: {p['likes']} | Комменты: {p['comments']}\n"
                f"   Engagement Rate (ER): {p['er']}% | Дата замера: {p['date']}\n"
                f"   Ссылка: {p['url']}\n\n"
            )
        return summary_text

    def generate_plan(self) -> str:
        """
        Собирает аналитику, отправляет ее в OpenAI и генерирует контент-план.
        """
        if not self.client:
            logger.error("[PLANNER] OpenAI клиент не инициализирован (проверьте OPENAI_API_KEY)!")
            return "Ошибка: не настроен OPENAI_API_KEY."

        logger.info("[PLANNER] Сбор лучших показателей контента для анализа...")
        historical_summary = self.get_best_performing_content()
        
        logger.info("[PLANNER] Отправка запроса к OpenAI GPT...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Вот статистика нашего контента:\n\n{historical_summary}\n\nСоставь контент-план на следующие 7 дней."}
                ],
                temperature=0.7,
                timeout=60
            )
            
            plan_content = response.choices[0].message.content
            
            # Сохраняем сгенерированный план локально
            date_str = datetime.now().strftime("%Y-%m-%d")
            plan_file_path = os.path.join(self.plans_dir, f"plan_{date_str}.md")
            
            with open(plan_file_path, "w", encoding="utf-8") as f:
                f.write(plan_content)
                
            logger.info(f"[PLANNER] Контент-план успешно сгенерирован и сохранен в {os.path.basename(plan_file_path)}")
            return plan_content
            
        except Exception as e:
            logger.error(f"[PLANNER] Ошибка генерации контент-плана: {str(e)}")
            return f"Ошибка при генерации контент-плана: {str(e)}"

if __name__ == "__main__":
    planner = AIContentPlanner()
    plan = planner.generate_plan()
    print("\n--- СГЕНЕРИРОВАННЫЙ КОНТЕНТ-ПЛАН ---")
    print(plan)
