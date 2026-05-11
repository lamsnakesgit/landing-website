import os
import aiohttp
import logging

async def upload_to_catbox(file_path):
    """
    Загружает файл на catbox.moe для получения прямой ссылки
    """
    url = "https://catbox.moe/user/api.php"
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('reqtype', 'fileupload')
            # Важно: закрывать файл после использования
            with open(file_path, 'rb') as f:
                data.add_field('fileToUpload', f)
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        return await response.text()
                    logging.error(f"Catbox upload failed: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Error uploading to Catbox: {e}")
        return None

def setup_logging():
    """
    Базовая настройка логирования
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler("../logs/bot.log"),
            logging.StreamHandler()
        ]
    )
