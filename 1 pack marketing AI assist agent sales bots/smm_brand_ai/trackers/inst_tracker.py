import os
import json
import requests
from datetime import datetime
from .base_tracker import BaseTracker

class InstagramTracker(BaseTracker):
    def __init__(self):
        super().__init__("instagram")
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.session_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "database", 
            "instagram_session.json"
        )

    def track_profile_via_rapidapi(self, target_username: str, limit: int = 12):
        """
        Сбор метрик профиля через RapidAPI (Instagram Bulk Scraper).
        Это надежный способ парсить открытые профили без ввода своего пароля.
        """
        if not self.rapidapi_key:
            self.log_error("RapidAPI ключ не настроен (отсутствует RAPIDAPI_KEY)")
            return False

        self.log_info(f"Начало сбора метрик для Instagram @{target_username} через RapidAPI...")
        url = "https://instagram-bulk-scraper-latest.p.rapidapi.com/get_user_posts"
        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "instagram-bulk-scraper-latest.p.rapidapi.com"
        }
        params = {"username": target_username}

        try:
            res = requests.get(url, headers=headers, params=params, timeout=20)
            if res.status_code != 200:
                self.log_error(f"RapidAPI вернул код {res.status_code}: {res.text}")
                return False

            data = res.json().get("data", {})
            posts = data.get("edges", [])
            
            self.log_info(f"Найдено {len(posts)} постов в профиле.")
            count = 0
            for edge in posts[:limit]:
                node = edge.get("node", {})
                post_id = node.get("id")
                shortcode = node.get("shortcode")
                post_url = f"https://www.instagram.com/p/{shortcode}/"
                
                # Текст поста
                caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                title = caption_edges[0]["node"]["text"][:100] if caption_edges else "Без описания"
                title = title.replace("\n", " ").strip()
                
                # Дата
                timestamp = node.get("taken_at_timestamp")
                publish_date = datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.now().isoformat()
                
                # Метрики
                views = node.get("video_view_count", 0)  # для Reels/видео
                likes = node.get("edge_liked_by", {}).get("count", 0)
                comments = node.get("edge_media_to_comment", {}).get("count", 0)
                
                # Сохраняем
                self.save_post(post_id, title, post_url, publish_date)
                self.save_metrics(
                    post_id=post_id,
                    views=max(views, likes),  # Для фото просмотры делаем равными лайкам как fallback
                    likes=likes,
                    comments=comments
                )
                count += 1
                
            self.log_info(f"Успешно обработано {count} постов через RapidAPI.")
            return True
        except Exception as e:
            self.log_error(f"Исключение при RapidAPI-трекинге Instagram: {str(e)}")
            return False

    def track_profile_via_instagrapi(self, limit: int = 12):
        """
        Сбор метрик своего аккаунта через instagrapi (приватное API).
        Позволяет собирать не только посты, но и активные истории (Stories).
        """
        if not self.username or not self.password:
            self.log_error("Для instagrapi не заданы INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD")
            return False

        self.log_info(f"Начало сбора метрик для Instagram @{self.username} через instagrapi...")
        try:
            from instagrapi import Client
            cl = Client()
            
            # Загружаем сессию, если она есть, чтобы не логиниться заново
            if os.path.exists(self.session_path):
                try:
                    cl.load_settings(self.session_path)
                    self.log_info("Сессия Instagram успешно загружена из файла.")
                except Exception:
                    self.log_info("Не удалось загрузить сессию, выполняем чистый вход.")
            
            cl.login(self.username, self.password)
            cl.dump_settings(self.session_path)
            
            user_id = cl.user_id
            
            # 1. Сбор метрик по обычным постам и Reels
            medias = cl.user_medias(user_id, amount=limit)
            self.log_info(f"Через instagrapi загружено {len(medias)} постов/Reels.")
            
            for media in medias:
                post_id = media.id
                post_url = f"https://www.instagram.com/p/{media.code}/"
                title = media.caption_text[:100] if media.caption_text else "Без описания"
                title = title.replace("\n", " ").strip()
                publish_date = media.taken_at.isoformat()
                
                # Метрики
                views = media.view_count or 0
                likes = media.like_count or 0
                comments = media.comment_count or 0
                
                self.save_post(post_id, title, post_url, publish_date)
                self.save_metrics(
                    post_id=post_id,
                    views=max(views, likes),
                    likes=likes,
                    comments=comments
                )

            # 2. Сбор метрик по активным историям (Stories)
            # Внимание: истории доступны только по своему аккаунту!
            try:
                stories = cl.user_stories(user_id)
                self.log_info(f"Найдено активных Stories: {len(stories)}")
                for story in stories:
                    story_id = story.id
                    story_url = f"https://instagram.com/stories/{self.username}/{story_id.split('_')[0]}/"
                    title = f"[STORY] {story.caption_text[:50]}" if story.caption_text else "[STORY] Без текста"
                    publish_date = story.taken_at.isoformat()
                    
                    # Метрики истории (в instagrapi просмотры историй лежат в viewer_count)
                    views = story.viewer_count or 0
                    
                    # Сбор лайков истории (если они поддерживаются в объекте медиа)
                    likes = getattr(story, 'like_count', 0) or 0
                    
                    # Сохраняем историю
                    self.save_post(story_id, title, story_url, publish_date)
                    self.save_metrics(
                        post_id=story_id,
                        views=views,
                        likes=likes,
                        comments=0
                    )
            except Exception as story_err:
                self.log_error(f"Не удалось собрать метрики Stories: {str(story_err)}")
                
            return True
        except Exception as e:
            self.log_error(f"Ошибка instagrapi при сборе метрик: {str(e)}")
            return False

    def track_profile(self, target_username: str = None, limit: int = 12) -> bool:
        """
        Основной метод трекинга Instagram.
        Если target_username совпадает с логином или не задан — пробует instagrapi.
        Для сбора чужих профилей использует RapidAPI.
        """
        if not target_username:
            target_username = self.username
            
        # Убираем @
        if target_username:
            target_username = target_username.lstrip("@")
            
        # Если собираем себя и есть логин/пароль — используем instagrapi (так как это дает истории)
        if target_username == self.username and self.username and self.password:
            return self.track_profile_via_instagrapi(limit)
            
        # Иначе используем RapidAPI
        if self.rapidapi_key and target_username:
            return self.track_profile_via_rapidapi(target_username, limit)
            
        self.log_error("Недостаточно данных для запуска трекинга Instagram (нет ключей API или данных авторизации)")
        return False
