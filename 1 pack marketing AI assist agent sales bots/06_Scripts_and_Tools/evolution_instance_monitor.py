import os
import time
import json
from datetime import datetime

import requests
from dotenv import load_dotenv
from loguru import logger


load_dotenv()

os.makedirs("logs", exist_ok=True)
os.makedirs("scratch", exist_ok=True)

logger.add(
    "logs/evolution_instance_monitor.log",
    rotation="20 MB",
    retention="14 days",
    level="INFO",
)

EVOLUTION_BASE_URL = os.getenv("EVOLUTION_BASE_URL", "").rstrip("/")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "").strip().rstrip(".")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "").strip()

TELEGRAM_BOT_TOKEN = (
    os.getenv("NOTIFICATION_BOT_TOKEN")
    or os.getenv("TG_REALSTATE_SMM_BOT")
    or os.getenv("TELEGRAM_BOT_TOKEN")
)
TELEGRAM_CHAT_ID = (
    os.getenv("TG_REALSTATE_SMM_CHAT_ID")
    or os.getenv("TELEGRAM_CHAT_ID")
    or os.getenv("TG_CHAT_ID")
    or "888005446"
)

POLL_SECONDS = int(os.getenv("EVOLUTION_MONITOR_POLL_SECONDS", "60"))
ALERT_COOLDOWN_SECONDS = int(os.getenv("EVOLUTION_MONITOR_ALERT_COOLDOWN_SECONDS", "900"))
STATE_FILE = os.getenv(
    "EVOLUTION_MONITOR_STATE_FILE",
    "scratch/evolution_monitor_state.json",
)
REQUEST_TIMEOUT = int(os.getenv("EVOLUTION_MONITOR_TIMEOUT_SECONDS", "20"))

BAD_STATUSES = {
    "close",
    "closed",
    "disconnected",
    "disconnect",
    "notconnected",
    "not_connected",
    "offline",
    "error",
}


def load_state():
    """Читает сохранённое состояние мониторинга с диска."""
    if not os.path.exists(STATE_FILE):
        return {"instances": {}, "last_global_error_alert_at": None}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as error:
        logger.warning(f"Не удалось прочитать state-файл: {error}")
        return {"instances": {}, "last_global_error_alert_at": None}


def save_state(state):
    """Сохраняет состояние мониторинга на диск."""
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)


def now_iso():
    """Возвращает текущее время в ISO-формате."""
    return datetime.utcnow().isoformat() + "Z"


def normalize_status(raw_status):
    """Нормализует статус инстанса для сравнения и алертов."""
    if raw_status is None:
        return "unknown"
    return str(raw_status).strip().lower().replace(" ", "_")


def send_telegram_message(text):
    """Отправляет уведомление в Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram не настроен. Уведомление пропущено.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return True
    except Exception as error:
        logger.error(f"Ошибка отправки Telegram-уведомления: {error}")
        return False


def fetch_instances():
    """Запрашивает список инстансов из Evolution API."""
    url = f"{EVOLUTION_BASE_URL}/instance/fetchInstances"
    headers = {"apikey": EVOLUTION_API_KEY}
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def extract_instances(raw_data):
    """Приводит ответ Evolution API к единому списку инстансов."""
    if isinstance(raw_data, list):
        return raw_data

    if isinstance(raw_data, dict):
        for key in ["data", "instances", "result"]:
            value = raw_data.get(key)
            if isinstance(value, list):
                return value

    return []


def parse_instance_record(item):
    """Извлекает имя, статус и диагностическую информацию по инстансу."""
    instance = item.get("instance") if isinstance(item.get("instance"), dict) else item
    connection = item.get("connectionStatus") if isinstance(item.get("connectionStatus"), dict) else {}

    instance_name = (
        instance.get("instanceName")
        or item.get("instanceName")
        or item.get("name")
        or "unknown"
    )
    status_raw = (
        instance.get("status")
        or connection.get("state")
        or connection.get("status")
        or item.get("status")
        or item.get("state")
        or "unknown"
    )
    owner = instance.get("owner") or item.get("owner") or "-"
    profile_name = instance.get("profileName") or item.get("profileName") or "-"

    reason_parts = []
    for key in [
        "statusReason",
        "reason",
        "message",
        "error",
        "disconnectedReason",
    ]:
        value = item.get(key)
        if value:
            reason_parts.append(f"{key}={value}")

    if connection:
        for key in ["state", "status", "message", "reason"]:
            value = connection.get(key)
            if value:
                reason_parts.append(f"connection.{key}={value}")

    return {
        "instance_name": instance_name,
        "status": normalize_status(status_raw),
        "status_raw": status_raw,
        "owner": owner,
        "profile_name": profile_name,
        "reason": " | ".join(dict.fromkeys(reason_parts)) if reason_parts else "Причина не пришла в API",
        "raw": item,
    }


def should_alert(last_alert_at):
    """Проверяет, можно ли снова слать алерт с учётом cooldown."""
    if not last_alert_at:
        return True

    try:
        previous_ts = datetime.fromisoformat(last_alert_at.replace("Z", "+00:00")).timestamp()
        return time.time() - previous_ts >= ALERT_COOLDOWN_SECONDS
    except Exception:
        return True


def build_down_message(record):
    """Собирает текст тревожного уведомления."""
    return (
        "🚨 <b>Evolution instance проблема</b>\n"
        f"• Инстанс: <code>{record['instance_name']}</code>\n"
        f"• Статус: <code>{record['status_raw']}</code>\n"
        f"• Владелец: <code>{record['owner']}</code>\n"
        f"• Профиль: <code>{record['profile_name']}</code>\n"
        f"• Причина: <code>{record['reason'][:2500]}</code>\n"
        f"• Время: <code>{now_iso()}</code>"
    )


def build_recovery_message(record):
    """Собирает текст уведомления о восстановлении."""
    return (
        "✅ <b>Evolution instance восстановился</b>\n"
        f"• Инстанс: <code>{record['instance_name']}</code>\n"
        f"• Текущий статус: <code>{record['status_raw']}</code>\n"
        f"• Время: <code>{now_iso()}</code>"
    )


def monitor_once(state):
    """Выполняет один цикл проверки всех инстансов."""
    raw_response = fetch_instances()
    instances = extract_instances(raw_response)
    logger.info(f"Получено инстансов от Evolution API: {len(instances)}")

    seen_names = set()

    for item in instances:
        record = parse_instance_record(item)
        instance_name = record["instance_name"]
        seen_names.add(instance_name)

        if EVOLUTION_INSTANCE and instance_name != EVOLUTION_INSTANCE:
            continue

        instance_state = state["instances"].get(instance_name, {})
        previous_status = instance_state.get("status")
        was_problem = instance_state.get("is_problem", False)
        is_problem = record["status"] in BAD_STATUSES or record["status"] == "unknown"

        logger.info(
            f"Инстанс={instance_name} status={record['status']} previous={previous_status} problem={is_problem}"
        )

        if is_problem:
            if (not was_problem) or (previous_status != record["status"]):
                if should_alert(instance_state.get("last_alert_at")):
                    send_telegram_message(build_down_message(record))
                    instance_state["last_alert_at"] = now_iso()
        elif was_problem:
            send_telegram_message(build_recovery_message(record))

        instance_state.update(
            {
                "status": record["status"],
                "status_raw": str(record["status_raw"]),
                "reason": record["reason"],
                "owner": record["owner"],
                "profile_name": record["profile_name"],
                "last_checked_at": now_iso(),
                "is_problem": is_problem,
            }
        )
        state["instances"][instance_name] = instance_state

    if EVOLUTION_INSTANCE and EVOLUTION_INSTANCE not in seen_names:
        instance_state = state["instances"].get(EVOLUTION_INSTANCE, {})
        if should_alert(instance_state.get("last_alert_at")):
            send_telegram_message(
                "🚨 <b>Evolution instance не найден в fetchInstances</b>\n"
                f"• Инстанс: <code>{EVOLUTION_INSTANCE}</code>\n"
                f"• Время: <code>{now_iso()}</code>"
            )
            instance_state["last_alert_at"] = now_iso()

        instance_state.update(
            {
                "status": "missing",
                "status_raw": "missing",
                "reason": "Инстанс отсутствует в ответе /instance/fetchInstances",
                "last_checked_at": now_iso(),
                "is_problem": True,
            }
        )
        state["instances"][EVOLUTION_INSTANCE] = instance_state

    return state


def main():
    """Запускает бесконечный цикл мониторинга Evolution instance."""
    if not EVOLUTION_BASE_URL or not EVOLUTION_API_KEY:
        raise RuntimeError("EVOLUTION_BASE_URL или EVOLUTION_API_KEY не заданы в .env")

    logger.info("=== Старт Evolution Instance Monitor ===")
    logger.info(f"API: {EVOLUTION_BASE_URL}")
    logger.info(f"Целевой инстанс: {EVOLUTION_INSTANCE or 'все инстансы'}")
    logger.info(f"Интервал проверки: {POLL_SECONDS} сек")

    state = load_state()

    while True:
        try:
            state = monitor_once(state)
            save_state(state)
        except Exception as error:
            logger.exception(f"Ошибка цикла мониторинга: {error}")
            if should_alert(state.get("last_global_error_alert_at")):
                send_telegram_message(
                    "🚨 <b>Evolution monitor упал на ошибке</b>\n"
                    f"• Ошибка: <code>{str(error)[:3000]}</code>\n"
                    f"• Время: <code>{now_iso()}</code>"
                )
                state["last_global_error_alert_at"] = now_iso()
                save_state(state)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()