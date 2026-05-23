import os
import json
from datetime import datetime
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class BaseTracker:
    def __init__(self, platform_name: str):
        self.platform = platform_name
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Локальный файл для резервного сохранения данных
        self.local_db_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "database"
        )
        os.makedirs(self.local_db_dir, exist_ok=True)
        self.local_db_path = os.path.join(self.local_db_dir, "local_smm_data.json")

    def log_info(self, message: str):
        logger.info(f"[{self.platform.upper()}] {message}")

    def log_error(self, message: str):
        logger.error(f"[{self.platform.upper()}] {message}")

    def save_post(self, post_id: str, title: str, url: str, publish_date: str = None) -> bool:
        """
        Сохраняет или обновляет информацию о посте в реестре smm_posts.
        """
        if not publish_date:
            publish_date = datetime.now().isoformat()

        post_data = {
            "platform": self.platform,
            "post_id": str(post_id),
            "title": title,
            "url": url,
            "publish_date": publish_date
        }

        # Если настроен Supabase, отправляем туда
        if self.supabase_url and self.supabase_key:
            url_endpoint = f"{self.supabase_url.rstrip('/')}/rest/v1/smm_posts"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            try:
                res = requests.post(url_endpoint, json=post_data, headers=headers, timeout=10)
                if res.status_code in [200, 201]:
                    self.log_info(f"Пост {post_id} успешно сохранен в Supabase.")
                    return True
                else:
                    self.log_error(f"Ошибка сохранения поста в Supabase ({res.status_code}): {res.text}")
            except Exception as e:
                self.log_error(f"Исключение при сохранении поста в Supabase: {str(e)}")

        # Сохранение в локальный JSON (как fallback или дублирование)
        return self._save_local("posts", f"{self.platform}_{post_id}", post_data)

    def save_metrics(self, post_id: str, views: int = 0, likes: int = 0, comments: int = 0, shares: int = 0, saves: int = 0, reactions_json: dict = None) -> bool:
        """
        Сохраняет ежедневные метрики поста в smm_metrics_history.
        """
        if reactions_json is None:
            reactions_json = {}

        # Расчет Engagement Rate (ER)
        # ER = ((Лайки + Комменты + Репосты + Сохранения) / Просмотры) * 100
        total_interactions = likes + comments + shares + saves
        er = 0.0
        if views > 0:
            er = round((total_interactions / views) * 100, 2)

        tracked_date = datetime.now().strftime("%Y-%m-%d")

        metrics_data = {
            "platform": self.platform,
            "post_id": str(post_id),
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "reactions_json": reactions_json,
            "er": er,
            "tracked_date": tracked_date
        }

        # Если настроен Supabase
        if self.supabase_url and self.supabase_key:
            url_endpoint = f"{self.supabase_url.rstrip('/')}/rest/v1/smm_metrics_history"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            try:
                res = requests.post(url_endpoint, json=metrics_data, headers=headers, timeout=10)
                if res.status_code in [200, 201]:
                    self.log_info(f"Метрики поста {post_id} от {tracked_date} сохранены в Supabase. ER: {er}%")
                    return True
                else:
                    self.log_error(f"Ошибка сохранения метрик в Supabase ({res.status_code}): {res.text}")
            except Exception as e:
                self.log_error(f"Исключение при сохранении метрик в Supabase: {str(e)}")

        # Сохранение в локальный JSON
        local_key = f"{self.platform}_{post_id}_{tracked_date}"
        return self._save_local("metrics", local_key, metrics_data)

    def _save_local(self, data_type: str, key: str, data: dict) -> bool:
        """
        Запись данных в локальный JSON файл.
        """
        try:
            db_data = {}
            if os.path.exists(self.local_db_path):
                with open(self.local_db_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)
            
            if data_type not in db_data:
                db_data[data_type] = {}
                
            db_data[data_type][key] = data

            with open(self.local_db_path, "w", encoding="utf-8") as f:
                json.dump(db_data, f, ensure_ascii=False, indent=4)
                
            self.log_info(f"Данные [{data_type}] для ключа {key} сохранены локально в {os.path.basename(self.local_db_path)}")
            return True
        except Exception as e:
            self.log_error(f"Ошибка записи в локальный JSON: {str(e)}")
            return False
