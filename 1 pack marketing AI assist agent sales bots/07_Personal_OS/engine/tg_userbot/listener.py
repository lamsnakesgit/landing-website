import os
import asyncio
from telethon import TelegramClient, events
from loguru import logger
from dotenv import load_dotenv

# Загружаем переменные окружения (API_ID и API_HASH берем из my.telegram.org)
load_dotenv()

API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
PHONE = os.getenv("TG_PHONE")

# Настройка логгера
logger.add("logs/tg_userbot.log", rotation="10 MB", retention="5 days", level="INFO")

client = TelegramClient('sessions/personal_os_bot', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    """Слушатель всех новых сообщений"""
    try:
        # Получаем текст сообщения и ID чата
        text = event.message.message
        chat_id = event.chat_id
        sender = await event.get_sender()
        
        # Логируем входящее (для отладки)
        # logger.info(f"Новое сообщение из {chat_id}: {text[:50]}...")

        # ЛОГИКА АНАЛИЗА (Сюда добавим вызов Gemini для поиска лидов)
        if text and len(text) > 10:
            # Пример: Ищем ключевые слова "нужен", "куплю", "ищу"
            keywords = ["нужен", "куплю", "ищу", "посоветуйте", "маркетолог", "ассистент"]
            if any(word in text.lower() for word in keywords):
                logger.warning(f"🔥 Найден потенциальный ЛИД в чате {chat_id}!")
                logger.info(f"Отправитель: {getattr(sender, 'username', 'Unknown')} | Текст: {text}")
                
                # ТУТ: Отправка в Supabase или уведомление в твой админ-канал
                # send_to_supabase(text, chat_id, sender)

    except Exception as e:
        logger.error(f"Ошибка в обработчике: {e}")

async def main():
    logger.info("Запуск TG Userbot Listener...")
    await client.start(phone=PHONE)
    logger.success("Userbot запущен и слушает чаты!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
