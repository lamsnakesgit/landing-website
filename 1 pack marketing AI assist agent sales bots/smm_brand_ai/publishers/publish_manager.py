import os
import argparse
from loguru import logger

# Импортируем публикаторы
from smm_brand_ai.publishers.wa_status_publisher import WhatsAppStatusPublisher
from smm_brand_ai.publishers.tg_story_publisher import TelegramStoryPublisher
from smm_brand_ai.publishers.inst_story_publisher import InstagramStoryPublisher

def publish_to_platforms(media_path: str, caption: str = "", platforms: list = None, tg_target: str = "me"):
    """
    Отправляет медиафайл в сторис на выбранные платформы.
    """
    if not platforms:
        platforms = ["whatsapp", "telegram"]

    logger.info(f"=== Запуск автопостинга Stories. Файл: {os.path.basename(media_path)} ===")
    logger.info(f"Целевые платформы: {', '.join(platforms)}")

    results = {}

    # Валидация файла
    if not os.path.exists(media_path):
        logger.error(f"Файл {media_path} не существует!")
        return {"error": f"Файл {media_path} не найден."}

    # 1. WhatsApp Status
    if "whatsapp" in platforms:
        logger.info("Публикация в WhatsApp...")
        publisher = WhatsAppStatusPublisher()
        success = publisher.publish_status(media_path, caption)
        results["whatsapp"] = "Успешно" if success else "Ошибка"

    # 2. Telegram Stories
    if "telegram" in platforms:
        logger.info(f"Публикация в Telegram (цель: {tg_target})...")
        publisher = TelegramStoryPublisher()
        success = publisher.publish_story(tg_target, media_path, caption)
        results["telegram"] = "Успешно" if success else "Ошибка"

    # 3. Instagram Stories
    if "instagram" in platforms:
        logger.info("Публикация в Instagram...")
        publisher = InstagramStoryPublisher()
        success = publisher.publish_story(media_path, caption)
        results["instagram"] = "Успешно" if success else "Ошибка"

    logger.info("=== Публикация Stories завершена ===")
    print("\n📋 ОТЧЕТ ПУБЛИКАЦИИ:")
    for platform, status in results.items():
        print(f"- {platform.capitalize()}: {status}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автопостинг сторис SMM Brand AI")
    parser.add_argument("--media", type=str, required=True, help="Путь к файлу картинки или видео (9:16)")
    parser.add_argument("--caption", type=str, default="", help="Подпись к сторис/статусу")
    parser.add_argument("--platforms", type=str, default="whatsapp,telegram", help="Платформы через запятую (whatsapp,telegram,instagram)")
    parser.add_argument("--tg_target", type=str, default="me", help="Telegram ID получателя (или 'me' для своего профиля)")
    args = parser.parse_args()

    platform_list = [p.strip().lower() for p in args.platforms.split(",")]
    
    # Делаем путь абсолютным, если передан относительный
    abs_media_path = os.path.abspath(args.media)

    publish_to_platforms(
        media_path=abs_media_path,
        caption=args.caption,
        platforms=platform_list,
        tg_target=args.tg_target
    )
