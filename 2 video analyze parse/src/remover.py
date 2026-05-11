import asyncio
import random
import os
import logging
from playwright.async_api import async_playwright

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

async def remove_provider_1(page, url, download_dir):
    """Стратегия для watermark-off.com"""
    logging.info(f"[*] Пробую watermark-off.com для {url}...")
    await page.goto("https://watermark-off.com/", wait_until="networkidle", timeout=30000)
    
    input_selector = 'input[placeholder*="Paste Sora video URL"]'
    await page.fill(input_selector, url)
    await page.click('button:has-text("REMOVE WATERMARK")')
    
    download_btn_selector = 'a:has-text("DOWNLOAD"), button:has-text("DOWNLOAD")'
    await page.wait_for_selector(download_btn_selector, timeout=60000)
    
    async with page.expect_download(timeout=60000) as download_info:
        await page.click(download_btn_selector)
    
    download = await download_info.value
    file_path = os.path.join(download_dir, download.suggested_filename)
    await download.save_as(file_path)
    return file_path

async def remove_provider_2(page, url, download_dir):
    """Стратегия для removesorawatermark.online"""
    logging.info(f"[*] Пробую removesorawatermark.online для {url}...")
    await page.goto("https://www.removesorawatermark.online/", wait_until="networkidle", timeout=30000)
    
    # Селектор из исследования: id="share-link"
    await page.fill('#share-link', url)
    # Кнопка: Remove Watermark Now
    await page.click('button:has-text("Remove Watermark Now")')
    
    # Ждем кнопку скачивания
    download_btn_selector = 'a:has-text("Download"), button:has-text("Download")'
    await page.wait_for_selector(download_btn_selector, timeout=60000)
    
    async with page.expect_download(timeout=60000) as download_info:
        await page.click(download_btn_selector)
        
    download = await download_info.value
    file_path = os.path.join(download_dir, download.suggested_filename)
    await download.save_as(file_path)
    return file_path

async def main_remover(url, download_dir):
    """Главная функция с системой Fallback"""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        providers = [remove_provider_1, remove_provider_2]
        result_file = None
        
        for i, provider in enumerate(providers):
            context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
            page = await context.new_page()
            try:
                result_file = await provider(page, url, download_dir)
                if result_file:
                    logging.info(f"[+] Успешно обработано провайдером {i+1}")
                    break
            except Exception as e:
                logging.error(f"[!] Ошибка провайдера {i+1}: {e}")
                # Скриншот ошибки
                error_shot = os.path.join(download_dir, f"error_prov_{i+1}.png")
                await page.screenshot(path=error_shot)
            finally:
                await context.close()
        
        await browser.close()
        if result_file:
            # Для n8n выводим ТОЛЬКО путь к файлу в последней строке
            print(result_file)
        return result_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        # Путь к загрузкам относительно корня проекта
        d_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../downloads"))
        asyncio.run(main_remover(target_url, d_dir))
    else:
        print("Использование: python3 src/remover.py <url>")
