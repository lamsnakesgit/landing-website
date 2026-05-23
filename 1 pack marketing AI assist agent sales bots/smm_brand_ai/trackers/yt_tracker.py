import os
import re
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from .base_tracker import BaseTracker

class YouTubeTracker(BaseTracker):
    def __init__(self):
        super().__init__("youtube")
        self.api_key = os.getenv("YOUTUBE_API_KEY")

    def track_channel_via_rss(self, channel_id: str):
        """
        Собирает метрики последних 15 видео канала БЕЗ API ключей через публичный официальный RSS фид YouTube.
        """
        self.log_info(f"Начало сбора метрик для канала {channel_id} через RSS...")
        
        # Если передан юзернейм с @, нам нужно получить ID канала.
        # Для простоты, если channel_id не начинается с "UC", предупреждаем.
        if not channel_id.startswith("UC"):
            # Попробуем найти channelId в коде главной страницы канала
            resolved_id = self._resolve_channel_id_from_username(channel_id)
            if resolved_id:
                channel_id = resolved_id
            else:
                self.log_error(f"Не удалось определить Channel ID для: {channel_id}. Нужен формат UC...")
                return False

        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200:
                self.log_error(f"Не удалось получить RSS фид канала {channel_id} ({res.status_code})")
                return False

            # Парсим XML
            root = ET.fromstring(res.content)
            
            # Пространства имен для парсинга
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'media': 'http://search.yahoo.com/mrss/',
                'yt': 'http://www.youtube.com/xml/schemas/2015'
            }

            entries = root.findall('atom:entry', ns)
            self.log_info(f"Найдено видео в RSS фиде: {len(entries)}")

            for entry in entries:
                try:
                    video_id = entry.find('yt:videoId', ns).text
                    post_url = f"https://www.youtube.com/watch?v={video_id}"
                    title = entry.find('atom:title', ns).text
                    
                    publish_date = entry.find('atom:published', ns).text
                    
                    # Извлекаем статистику из media:group
                    media_group = entry.find('media:group', ns)
                    views = 0
                    likes = 0
                    
                    if media_group is not None:
                        community = media_group.find('media:community', ns)
                        if community is not None:
                            # Просмотры
                            statistics = community.find('media:statistics', ns)
                            if statistics is not None:
                                views = int(statistics.get('views', 0))
                            
                            # Лайки (звездный рейтинг в RSS часто содержит лайки)
                            star_rating = community.find('media:starRating', ns)
                            if star_rating is not None:
                                # В RSS лайки иногда не передаются явно, но мы можем спарсить их отдельно или оставить 0
                                pass
                                
                    # Так как RSS не дает комменты и лайки на 100%, мы можем сделать легкий scraping страницы видео
                    likes, comments = self._scrape_video_page_metrics(video_id, fallback_likes=likes)

                    # Сохраняем пост в реестр
                    self.save_post(video_id, title, post_url, publish_date)
                    # Сохраняем метрики
                    self.save_metrics(
                        post_id=video_id,
                        views=views,
                        likes=likes,
                        comments=comments
                    )
                except Exception as e:
                    self.log_error(f"Ошибка парсинга видео из RSS: {str(e)}")
                    continue
                    
            return True
        except Exception as e:
            self.log_error(f"Исключение при RSS-трекинге канала {channel_id}: {str(e)}")
            return False

    def track_channel_via_api(self, channel_id: str, limit: int = 15):
        """
        Сбор метрик через официальный YouTube Data API v3
        """
        if not self.api_key:
            self.log_error("API-ключ YOUTUBE_API_KEY не настроен")
            return False
            
        self.log_info(f"Начало сбора метрик для канала {channel_id} через YouTube API...")
        
        # Если передан юзернейм с @
        if not channel_id.startswith("UC"):
            # Запрашиваем ID канала по юзернейму (handle)
            channel_id = self._resolve_channel_id_via_api(channel_id)
            if not channel_id:
                return False

        try:
            # 1. Получаем список последних видео (через поиск или playlist uploads)
            # Сначала получим uploads playlist ID для канала
            channel_url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "contentDetails",
                "id": channel_id,
                "key": self.api_key
            }
            res = requests.get(channel_url, params=params, timeout=10)
            res.raise_for_status()
            
            items = res.json().get("items", [])
            if not items:
                self.log_error(f"Канал {channel_id} не найден через API.")
                return False
                
            uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # 2. Получаем видео из плейлиста uploads
            playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet",
                "playlistId": uploads_playlist_id,
                "maxResults": limit,
                "key": self.api_key
            }
            res = requests.get(playlist_url, params=params, timeout=10)
            res.raise_for_status()
            
            video_items = res.json().get("items", [])
            self.log_info(f"Получено {len(video_items)} видео из плейлиста uploads.")
            
            video_ids = []
            video_details = {}
            
            for item in video_items:
                v_id = item["snippet"]["resourceId"]["videoId"]
                video_ids.append(v_id)
                video_details[v_id] = {
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={v_id}",
                    "publish_date": item["snippet"]["publishedAt"]
                }
                
            if not video_ids:
                return True
                
            # 3. Запрашиваем детальную статистику для всех видео пачкой
            videos_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": self.api_key
            }
            res = requests.get(videos_url, params=params, timeout=10)
            res.raise_for_status()
            
            stats_items = res.json().get("items", [])
            for item in stats_items:
                v_id = item["id"]
                stats = item["statistics"]
                
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                comments = int(stats.get("commentCount", 0))
                
                details = video_details[v_id]
                
                # Сохраняем в реестр и метрики
                self.save_post(v_id, details["title"], details["url"], details["publish_date"])
                self.save_metrics(
                    post_id=v_id,
                    views=views,
                    likes=likes,
                    comments=comments
                )
                
            return True
        except Exception as e:
            self.log_error(f"Ошибка YouTube API: {str(e)}")
            return False

    def track_channel(self, channel_id: str, limit: int = 15) -> bool:
        """
        Основной метод трекинга: пробует API, при отсутствии ключа идет в RSS.
        """
        if self.api_key:
            success = self.track_channel_via_api(channel_id, limit)
            if success:
                return True
            self.log_info("Сбор через API завершился ошибкой. Пробуем RSS...")
            
        return self.track_channel_via_rss(channel_id)

    def _resolve_channel_id_from_username(self, username: str) -> str:
        """
        Парсит публичную страницу канала для извлечения channelId (UC...)
        """
        username = username.lstrip("@")
        url = f"https://www.youtube.com/@{username}"
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if res.status_code == 200:
                # Ищем подстроку "browseId":"UC..." или "channelId":"UC..."
                match = re.search(r'"browseId"\s*:\s*"(UC[a-zA-Z0-9_-]{22})"', res.text)
                if match:
                    channel_id = match.group(1)
                    self.log_info(f"Определен Channel ID {channel_id} для юзернейма @{username}")
                    return channel_id
        except Exception as e:
            self.log_error(f"Не удалось разрешить юзернейм @{username} через веб: {str(e)}")
        return ""

    def _resolve_channel_id_via_api(self, username: str) -> str:
        """
        Ищет ID канала по юзернейму (handle) через API поиск
        """
        username = username.lstrip("@")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": f"@{username}",
            "type": "channel",
            "key": self.api_key
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            items = res.json().get("items", [])
            if items:
                channel_id = items[0]["snippet"]["channelId"]
                self.log_info(f"API определил Channel ID {channel_id} для @{username}")
                return channel_id
        except Exception as e:
            self.log_error(f"Не удалось разрешить юзернейм @{username} через API: {str(e)}")
        return ""

    def _scrape_video_page_metrics(self, video_id: str, fallback_likes: int = 0) -> tuple:
        """
        Легкий скрейпинг веб-страницы видео для получения лайков и комментов, если нет API.
        """
        likes = fallback_likes
        comments = 0
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            # Делаем запрос с английским языком, чтобы регулярки парсили корректно
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9"
            }
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                html = res.text
                
                # Поиск лайков в JSON-структурах страницы (YT рендерит данные через ytInitialData)
                # Ищем что-то вроде "label":"12,345 likes"
                likes_match = re.search(r'"label"\s*:\s*"([\d,]+)\s+likes"', html)
                if likes_match:
                    likes = int(re.sub(r'[^\d]', '', likes_match.group(1)))
                
                # Ищем количество комментариев: "commentCount":{"simpleText":"1,234"}
                comments_match = re.search(r'"commentCount"\s*:\s*\{\s*"simpleText"\s*:\s*"([\d,]+)"\}', html)
                if comments_match:
                    comments = int(re.sub(r'[^\d]', '', comments_match.group(1)))
        except Exception:
            pass  # Возвращаем дефолтные значения при любой ошибке
            
        return likes, comments
