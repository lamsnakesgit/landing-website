import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base_tracker import BaseTracker

class TelegramTracker(BaseTracker):
    def __init__(self):
        super().__init__("telegram")
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.session_name = os.getenv("TELEGRAM_SESSION_NAME", "smm_brand_ai_session")

    def track_channel_via_web(self, channel_username: str, limit: int = 10):
        """
        Собирает метрики последних постов публичного канала БЕЗ API ключей через публичный веб-интерфейс t.me/s/
        """
        self.log_info(f"Начало сбора метрик для канала @{channel_username} через веб...")
        url = f"https://t.me/s/{channel_username}"
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if res.status_code != 200:
                self.log_error(f"Не удалось получить веб-страницу канала @{channel_username} ({res.status_code})")
                return False

            soup = BeautifulSoup(res.text, "html.parser")
            post_elements = soup.find_all("div", class_="tgme_widget_message")
            
            if not post_elements:
                self.log_error(f"Не найдены посты на веб-странице канала @{channel_username}")
                return False

            # Берем последние посты (с конца)
            latest_posts = post_elements[-limit:]
            self.log_info(f"Найдено постов на странице: {len(post_elements)}, обрабатываем последние {len(latest_posts)}")

            for post in latest_posts:
                try:
                    # Извлекаем ID поста из атрибута data-post
                    post_data_attr = post.get("data-post")
                    if not post_data_attr or "/" not in post_data_attr:
                        continue
                    
                    post_id = post_data_attr.split("/")[-1]
                    post_url = f"https://t.me/{channel_username}/{post_id}"

                    # Текст поста (title)
                    text_elem = post.find("div", class_="tgme_widget_message_text")
                    title = text_elem.get_text()[:100] if text_elem else "Без текста"
                    # Очищаем текст от лишних пробелов
                    title = re.sub(r'\s+', ' ', title).strip()

                    # Дата публикации
                    time_elem = post.find("time", class_="time")
                    publish_date = time_elem.get("datetime") if time_elem else datetime.now().isoformat()

                    # Количество просмотров (views)
                    views_elem = post.find("span", class_="tgme_widget_message_views")
                    views = self._parse_number(views_elem.text if views_elem else "0")

                    # Количество комментариев (replies)
                    replies_elem = post.find("span", class_="tgme_widget_message_replies_number")
                    comments = self._parse_number(replies_elem.text if replies_elem else "0")

                    # Реакции
                    reactions = {}
                    reactions_container = post.find("div", class_="tgme_widget_message_reactions")
                    likes = 0
                    if reactions_container:
                        reaction_tags = reactions_container.find_all("a", class_="tgme_widget_message_reaction")
                        for tag in reaction_tags:
                            # Достаем эмодзи реакции
                            emoji_elem = tag.find("i", class_="tgme_widget_message_reaction_emoji")
                            emoji = emoji_elem.text if emoji_elem else ""
                            # Достаем число
                            count_elem = tag.find("span", class_="tgme_widget_message_reaction_count")
                            count = self._parse_number(count_elem.text if count_elem else "0")
                            
                            if emoji:
                                reactions[emoji] = count
                                likes += count  # Суммируем все реакции как лайки для универсальной метрики

                    # Сохраняем пост в реестр
                    self.save_post(post_id, title, post_url, publish_date)
                    # Сохраняем метрики
                    self.save_metrics(
                        post_id=post_id,
                        views=views,
                        likes=likes,
                        comments=comments,
                        reactions_json=reactions
                    )
                except Exception as e:
                    self.log_error(f"Ошибка парсинга конкретного поста: {str(e)}")
                    continue
            
            return True
        except Exception as e:
            self.log_error(f"Исключение при веб-трекинге канала @{channel_username}: {str(e)}")
            return False

    def track_channel_via_telethon(self, channel_username: str, limit: int = 10):
        """
        Сбор метрик через Telethon (если настроены доступы)
        """
        if not self.api_id or not self.api_hash:
            self.log_error("Telethon не настроен (отсутствуют TELEGRAM_API_ID/TELEGRAM_API_HASH)")
            return False
        
        self.log_info(f"Начало сбора метрик для канала @{channel_username} через Telethon...")
        try:
            from telethon import TelegramClient
            from telethon.tl.types import MessageActionChatCreate
            
            client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)
            
            async def run():
                await client.start()
                entity = await client.get_entity(channel_username)
                
                async for message in client.iter_messages(entity, limit=limit):
                    if not message or getattr(message, 'action', None):
                        continue
                    
                    post_id = message.id
                    post_url = f"https://t.me/{channel_username}/{post_id}"
                    
                    # Извлекаем текст
                    title = message.text[:100] if message.text else "Без текста"
                    title = re.sub(r'\s+', ' ', title).strip()
                    
                    publish_date = message.date.isoformat()
                    views = message.views or 0
                    
                    comments = 0
                    if message.replies:
                        comments = message.replies.replies or 0
                        
                    # Пересылки
                    shares = message.forwards or 0
                    
                    # Реакции
                    likes = 0
                    reactions = {}
                    if message.reactions:
                        for r in message.reactions.results:
                            emoji = getattr(r.reaction, 'emoticon', None)
                            if emoji:
                                count = r.count
                                reactions[emoji] = count
                                likes += count
                                
                    self.save_post(post_id, title, post_url, publish_date)
                    self.save_metrics(
                        post_id=post_id,
                        views=views,
                        likes=likes,
                        comments=comments,
                        shares=shares,
                        reactions_json=reactions
                    )
            
            with client:
                client.loop.run_until_complete(run())
            return True
        except Exception as e:
            self.log_error(f"Ошибка Telethon при сборе метрик: {str(e)}")
            return False

    def track_channel(self, channel_username: str, limit: int = 10) -> bool:
        """
        Основной метод трекинга: сначала пытается через Telethon, если он настроен,
        иначе автоматически переключается на веб-парсинг.
        """
        # Убираем собачку из юзернейма, если она есть
        channel_username = channel_username.lstrip("@")
        
        if self.api_id and self.api_hash:
            success = self.track_channel_via_telethon(channel_username, limit)
            if success:
                return True
            self.log_info("Telethon-сбор завершился неудачно. Пробуем через Web...")
            
        return self.track_channel_via_web(channel_username, limit)

    def _parse_number(self, val_str: str) -> int:
        """
        Конвертирует строки вида '1.2K', '3.5M' в целые числа.
        """
        val_str = val_str.upper().strip()
        val_str = val_str.replace(" ", "")
        
        if not val_str:
            return 0
            
        try:
            if "K" in val_str:
                num = float(val_str.replace("K", ""))
                return int(num * 1000)
            elif "M" in val_str:
                num = float(val_str.replace("M", ""))
                return int(num * 1000000)
            
            # Убираем все нецифровые символы
            clean_str = re.sub(r'[^\d]', '', val_str)
            return int(clean_str) if clean_str else 0
        except ValueError:
            return 0
