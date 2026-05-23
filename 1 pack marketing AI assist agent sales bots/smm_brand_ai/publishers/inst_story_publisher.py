import os
import mimetypes
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class InstagramStoryPublisher:
    def __init__(self):
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.session_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "database", 
            "instagram_session.json"
        )

    def publish_story(self, media_path: str, caption: str = "") -> bool:
        """
        Публикует сторис в Instagram через библиотеку instagrapi.
        Автоматически определяет тип медиа (фото/видео).
        """
        if not self.username or not self.password:
            logger.error("[INST_PUBLISHER] Ошибка: INSTAGRAM_USERNAME или INSTAGRAM_PASSWORD не заданы в .env!")
            return False

        if not os.path.exists(media_path):
            logger.error(f"[INST_PUBLISHER] Файл не найден: {media_path}")
            return False

        mime_type, _ = mimetypes.guess_type(media_path)
        if not mime_type:
            logger.error(f"[INST_PUBLISHER] Не удалось определить MIME-тип для: {media_path}")
            return False

        is_video = mime_type.startswith("video/")
        
        logger.info("[INST_PUBLISHER] Инициализация instagrapi клиента...")
        try:
            from instagrapi import Client
            cl = Client()
            
            # Попытка загрузить сессию
            if os.path.exists(self.session_path):
                try:
                    cl.load_settings(self.session_path)
                    logger.info("[INST_PUBLISHER] Сессия Instagram загружена.")
                except Exception:
                    logger.info("[INST_PUBLISHER] Ошибка загрузки сессии, будет выполнен полный вход.")
            
            # Вход (instagrapi сама проверит, жива ли сессия, если загружена)
            cl.login(self.username, self.password)
            # Сохраняем сессию на будущее
            cl.dump_settings(self.session_path)
            
            logger.info(f"[INST_PUBLISHER] Выполнен вход под пользователем: {self.username}")
            
            if is_video:
                logger.info(f"[INST_PUBLISHER] Загрузка видео-сторис {os.path.basename(media_path)}...")
                # instagrapi требует Path-объекты в некоторых версиях, передаем строку или Path
                from pathlib import Path
                media_path_obj = Path(media_path)
                
                # Загружаем видео в сторис
                story = cl.video_upload_to_story(media_path_obj, caption=caption)
                logger.info(f"[INST_PUBLISHER] Видео-сторис опубликована! ID: {story.id}")
            else:
                logger.info(f"[INST_PUBLISHER] Загрузка фото-сторис {os.path.basename(media_path)}...")
                from pathlib import Path
                media_path_obj = Path(media_path)
                
                # Загружаем фото в сторис
                story = cl.photo_upload_to_story(media_path_obj, caption=caption)
                logger.info(f"[INST_PUBLISHER] Фото-сторис опубликована! ID: {story.id}")
                
            return True
        except Exception as e:
            logger.error(f"[INST_PUBLISHER] Ошибка instagrapi при публикации: {str(e)}")
            return False
