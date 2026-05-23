import os
import asyncio
import requests
import mimetypes
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class TelegramStoryPublisher:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.session_name = os.getenv("TELEGRAM_SESSION_NAME", "smm_brand_ai_session")

    def publish_to_channel_via_bot(self, channel_chat_id: str, media_path: str, caption: str = "") -> bool:
        """
        Публикация истории в канал через Bot API (нужны бусты канала и права администратора у бота).
        Метод: sendChatStory (поддерживается в Telegram Bot API для фото и видео).
        """
        if not self.bot_token:
            logger.error("[TG_PUBLISHER] TELEGRAM_BOT_TOKEN не задан в .env!")
            return False

        if not os.path.exists(media_path):
            logger.error(f"[TG_PUBLISHER] Файл не найден: {media_path}")
            return False

        mime_type, _ = mimetypes.guess_type(media_path)
        if not mime_type:
            return False

        is_video = mime_type.startswith("video/")
        
        # Telegram Bot API sendChatStory endpoint
        url = f"https://api.telegram.org/bot{self.bot_token}/sendChatStory"
        
        payload = {
            "chat_id": channel_chat_id,
            "caption": caption
        }

        # Открываем файл для отправки
        file_key = "video" if is_video else "photo"
        try:
            with open(media_path, "rb") as f:
                files = {file_key: f}
                logger.info(f"[TG_PUBLISHER] Отправка истории в канал {channel_chat_id} через Bot API...")
                res = requests.post(url, data=payload, files=files, timeout=60)
                
                if res.status_code == 200:
                    logger.info("[TG_PUBLISHER] История успешно опубликована в канал!")
                    return True
                else:
                    logger.error(f"[TG_PUBLISHER] Ошибка Bot API ({res.status_code}): {res.text}")
                    return False
        except Exception as e:
            logger.error(f"[TG_PUBLISHER] Исключение при отправке через Bot API: {str(e)}")
            return False

    def publish_to_user_via_telethon(self, media_path: str, caption: str = "") -> bool:
        """
        Публикация истории в ЛИЧНЫЙ профиль пользователя через Telethon (юзербот).
        Использует вызовы MTProto API.
        """
        if not self.api_id or not self.api_hash:
            logger.error("[TG_PUBLISHER] TELEGRAM_API_ID или TELEGRAM_API_HASH не заданы!")
            return False

        if not os.path.exists(media_path):
            logger.error(f"[TG_PUBLISHER] Файл не найден: {media_path}")
            return False

        logger.info("[TG_PUBLISHER] Инициализация Telethon для публикации истории в профиль...")
        try:
            from telethon import TelegramClient, functions, types
            
            client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)
            
            async def run():
                await client.start()
                
                # Загружаем медиафайл на сервер Telegram
                logger.info("[TG_PUBLISHER] Загрузка файла в Telegram...")
                uploaded_file = await client.upload_file(media_path)
                
                mime_type, _ = mimetypes.guess_type(media_path)
                is_video = mime_type.startswith("video/") if mime_type else False

                # Формируем объект медиа для истории
                if is_video:
                    media = types.InputMediaUploadedDocument(
                        file=uploaded_file,
                        mime_type=mime_type or "video/mp4",
                        attributes=[types.DocumentAttributeVideo(
                            duration=15, # примерная длительность
                            w=720,
                            h=1280
                        )]
                    )
                else:
                    media = types.InputMediaUploadedPhoto(file=uploaded_file)

                # Публикация истории (к себе в профиль - peer='me')
                # Используем SendStoryRequest
                logger.info("[TG_PUBLISHER] Отправка запроса SendStoryRequest...")
                result = await client(functions.stories.SendStoryRequest(
                    peer='me',
                    media=media,
                    caption=caption,
                    privacy_rules=[types.InputPrivacyValueAllowAll()], # Доступно всем
                    period=86400 # 24 часа
                ))
                logger.info(f"[TG_PUBLISHER] История успешно опубликована в профиль! ID: {result.updates[0].id if result.updates else 'Успех'}")
                return True

            with client:
                client.loop.run_until_complete(run())
            return True
        except Exception as e:
            logger.error(f"[TG_PUBLISHER] Ошибка Telethon при публикации истории: {str(e)}")
            return False

    def publish_story(self, target: str, media_path: str, caption: str = "") -> bool:
        """
        Основной метод публикации.
        Если target = 'me' или юзернейм профиля — публикует через Telethon к себе в профиль.
        Если target начинается с '-' (ID канала) или это юзернейм канала (и бот там админ) — публикует через Bot API.
        """
        if target == "me" or not target.startswith("-"):
            # Публикация в профиль пользователя
            return self.publish_to_user_via_telethon(media_path, caption)
        else:
            # Публикация в канал
            return self.publish_to_channel_via_bot(target, media_path, caption)
ZOOM_LINK_EXTRACTOR = None
