import os
import base64
import requests
import mimetypes
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class WhatsAppStatusPublisher:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_BASE_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance = os.getenv("EVOLUTION_INSTANCE", "wa 1")

    def publish_status(self, media_path: str, caption: str = "") -> bool:
        """
        Публикует статус в WhatsApp (изображение или видео) через Evolution API.
        """
        if not self.base_url or not self.api_key:
            logger.error("[WA_PUBLISHER] Ошибка: EVOLUTION_BASE_URL или EVOLUTION_API_KEY не заданы в .env!")
            return False

        if not os.path.exists(media_path):
            logger.error(f"[WA_PUBLISHER] Файл не найден: {media_path}")
            return False

        # Определение типа файла
        mime_type, _ = mimetypes.guess_type(media_path)
        if not mime_type:
            logger.error(f"[WA_PUBLISHER] Не удалось определить MIME-тип файла: {media_path}")
            return False

        media_type = ""
        if mime_type.startswith("image/"):
            media_type = "image"
        elif mime_type.startswith("video/"):
            media_type = "video"
        else:
            logger.error(f"[WA_PUBLISHER] Неподдерживаемый тип медиа для сторис: {mime_type}")
            return False

        logger.info(f"[WA_PUBLISHER] Кодирование файла {os.path.basename(media_path)} в Base64...")
        try:
            with open(media_path, "rb") as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode("utf-8")
                # Формируем Data URI
                data_uri = f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            logger.error(f"[WA_PUBLISHER] Ошибка при чтении/кодировании файла: {str(e)}")
            return False

        # Эндпоинт отправки статуса в Evolution API
        # Обычно: POST /message/sendStatus/{instance}
        url = f"{self.base_url.rstrip('/')}/message/sendStatus/{self.instance}"
        
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "status": "status", # отправка всем контактам
            "type": media_type,
            "content": data_uri,
            "caption": caption
        }

        logger.info(f"[WA_PUBLISHER] Отправка запроса к Evolution API на инстанс '{self.instance}'...")
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=60)
            if res.status_code in [200, 201]:
                logger.info("[WA_PUBLISHER] Статус успешно опубликован в WhatsApp!")
                return True
            else:
                logger.error(f"[WA_PUBLISHER] Ошибка Evolution API ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            logger.error(f"[WA_PUBLISHER] Исключение при отправке статуса: {str(e)}")
            return False
