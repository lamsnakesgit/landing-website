import os
import json
import argparse
from loguru import logger

# Импортируем трекеры
from smm_brand_ai.trackers.tg_tracker import TelegramTracker
from smm_brand_ai.trackers.yt_tracker import YouTubeTracker
from smm_brand_ai.trackers.inst_tracker import InstagramTracker
from smm_brand_ai.trackers.tiktok_tracker import TikTokTracker

# Директории
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNTS_PATH = os.path.join(BASE_DIR, "database", "accounts.json")

def load_accounts():
    """Загружает список аккаунтов для отслеживания"""
    if not os.path.exists(ACCOUNTS_PATH):
        # Создаем дефолтный файл, если нет
        default_accounts = {
            "telegram": [],
            "youtube": [],
            "instagram": [],
            "tiktok": []
        }
        with open(ACCOUNTS_PATH, "w", encoding="utf-8") as f:
            json.dump(default_accounts, f, indent=4)
        return default_accounts
        
    with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_all(limit=10):
    logger.info("=== Запуск ежедневного сбора аналитики SMM ===")
    accounts = load_accounts()
    
    summary = []
    
    # 1. Telegram
    tg_accounts = accounts.get("telegram", [])
    if tg_accounts:
        logger.info(f"Запуск трекинга Telegram ({len(tg_accounts)} аккаунтов)...")
        tracker = TelegramTracker()
        for acc in tg_accounts:
            success = tracker.track_channel(acc, limit=limit)
            status = "Успешно" if success else "Ошибка"
            summary.append(f"Telegram (@{acc}): {status}")
            
    # 2. YouTube
    yt_accounts = accounts.get("youtube", [])
    if yt_accounts:
        logger.info(f"Запуск трекинга YouTube ({len(yt_accounts)} аккаунтов)...")
        tracker = YouTubeTracker()
        for acc in yt_accounts:
            success = tracker.track_channel(acc, limit=limit)
            status = "Успешно" if success else "Ошибка"
            summary.append(f"YouTube ({acc}): {status}")

    # 3. Instagram
    inst_accounts = accounts.get("instagram", [])
    if inst_accounts:
        logger.info(f"Запуск трекинга Instagram ({len(inst_accounts)} аккаунтов)...")
        tracker = InstagramTracker()
        for acc in inst_accounts:
            success = tracker.track_profile(acc, limit=limit)
            status = "Успешно" if success else "Ошибка"
            summary.append(f"Instagram (@{acc}): {status}")

    # 4. TikTok
    tt_accounts = accounts.get("tiktok", [])
    if tt_accounts:
        logger.info(f"Запуск трекинга TikTok ({len(tt_accounts)} аккаунтов)...")
        tracker = TikTokTracker()
        for acc in tt_accounts:
            success = tracker.track_profile(acc, limit=limit)
            status = "Успешно" if success else "Ошибка"
            summary.append(f"TikTok (@{acc}): {status}")

    logger.info("=== Сбор аналитики SMM завершен ===")
    print("\n📋 ИТОГОВЫЙ ОТЧЕТ СБОРА:")
    for line in summary:
        print(f"- {line}")
        
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сборщик аналитики SMM Brand AI")
    parser.add_argument("--limit", type=int, default=10, help="Лимит постов для сбора (по умолчанию 10)")
    args = parser.parse_args()
    
    run_all(limit=args.limit)
