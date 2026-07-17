import asyncio
import base64
import json
import logging
import os
from pathlib import Path

import websockets

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NCALayerMock")

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_dotenv_file(path: Path) -> None:
    """Минимально загружает .env без внешней зависимости и без вывода секретов в логи."""
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv_file(PROJECT_ROOT / ".env")

DEFAULT_KEY_PATH = "/Users/higherpower/Downloads/GOST512_28412edbee5073856db88468b73dbd8f53bb9636.p12"
KEY_PATH = os.getenv("TEST_KEY_PATH") or os.getenv("P12_PATH") or DEFAULT_KEY_PATH
KEY_PASSWORD = os.getenv("TEST_KEY_PASSWORD") or os.getenv("PASS_p12") or os.getenv("P12_PASSWORD") or ""
KALKAN_LIBRARY_PATH = os.getenv("KALKAN_LIBRARY_PATH", "libkalkancryptwr-64.so")
ALLOW_STUB_SIGNATURE = os.getenv("ALLOW_STUB_SIGNATURE", "false").lower() in {"1", "true", "yes"}

# Попытка импорта pykalkan. По PyPI/GitHub API выглядит как Adapter(lib).sign_data(base64).
try:
    from pykalkan import Adapter

    HAS_PYKALKAN = True
    logger.info("Библиотека pykalkan.Adapter успешно импортирована.")
except ImportError:
    Adapter = None
    HAS_PYKALKAN = False
    logger.warning("Библиотека pykalkan не найдена. Реальная подпись недоступна.")


def mask_path(path: str) -> str:
    """Не светим полный путь к ключу в логах."""
    if not path:
        return "<empty>"
    return str(Path(path).name)


def extract_base64_payload(data: dict) -> str:
    """
    В разных версиях NCALayer payload может приходить в args/arguments/data.
    Возвращаем первую похожую строку base64.
    """
    candidates = []

    for key in ("args", "arguments", "params"):
        value = data.get(key)
        if isinstance(value, list):
            candidates.extend(value)
        elif isinstance(value, dict):
            candidates.extend(value.values())

    for key in ("data", "base64", "payload", "xml"):
        if data.get(key):
            candidates.append(data.get(key))

    for candidate in candidates:
        if isinstance(candidate, str) and len(candidate.strip()) > 8:
            return candidate.strip()

    return ""


def sign_base64_payload(payload: str) -> str:
    """Подписывает base64 через pykalkan Adapter или явно падает с понятной ошибкой."""
    if not payload:
        raise ValueError("В запросе NCALayer не найден base64 payload для подписи.")

    if not Path(KEY_PATH).exists():
        raise FileNotFoundError(f"P12 key not found: {mask_path(KEY_PATH)}")

    if not KEY_PASSWORD:
        raise ValueError("Пароль P12 не найден в env: PASS_p12 / TEST_KEY_PASSWORD / P12_PASSWORD.")

    if not HAS_PYKALKAN:
        if ALLOW_STUB_SIGNATURE:
            logger.warning("ALLOW_STUB_SIGNATURE=true: возвращаем тестовую заглушку подписи.")
            return base64.b64encode(f"MOCK_SIGNATURE_FOR:{payload[:16]}".encode()).decode()
        raise RuntimeError("pykalkan не установлен. Установите pykalkan и KalkanCrypt SDK или включите ALLOW_STUB_SIGNATURE=true.")

    with Adapter(KALKAN_LIBRARY_PATH) as adapter:
        adapter.load_key_store(KEY_PATH, KEY_PASSWORD)
        try:
            adapter.set_tsa_url()
        except Exception as error:
            logger.warning(f"TSA URL не установлен, продолжаем подпись без остановки: {type(error).__name__}")

        signed_data = adapter.sign_data(payload)

    if isinstance(signed_data, bytes):
        return signed_data.decode("utf-8")

    return str(signed_data)


logger.info(
    "NCALayer config: key=%s key_exists=%s password_set=%s pykalkan=%s stub_allowed=%s",
    mask_path(KEY_PATH),
    Path(KEY_PATH).exists(),
    bool(KEY_PASSWORD),
    HAS_PYKALKAN,
    ALLOW_STUB_SIGNATURE,
)

async def handler(websocket):
    client_ip = websocket.remote_address
    logger.info(f"Новое подключение от: {client_ip}")
    
    try:
        async for message in websocket:
            logger.info(f"Получено сообщение: {message}")
            try:
                data = json.loads(message)
                module = data.get("module")
                method = data.get("method")
                
                # Имитация ответа от NCALayer
                response = {
                    "code": "500",
                    "message": "Not implemented in mock"
                }

                if method == "getActiveTokens":
                    # Возвращаем информацию, что доступно хранилище PKCS12 (файловый ключ)
                    response = {
                        "code": "200",
                        "responseObject": ["PKCS12"],
                        "message": "",
                        "result": "SUCCESS"
                    }
                elif method in {"createCAdESFromBase64", "createCMSSignatureFromBase64"}:
                    logger.info("Запрос на создание подписи: %s", method)
                    try:
                        payload = extract_base64_payload(data)
                        signed_payload = sign_base64_payload(payload)
                        response = {
                            "code": "200",
                            "responseObject": signed_payload,
                            "message": "",
                            "result": "SUCCESS"
                        }
                    except Exception as error:
                        logger.exception("Ошибка подписи NCALayer")
                        response = {
                            "code": "500",
                            "message": f"Signing failed: {type(error).__name__}: {error}",
                            "result": "ERROR"
                        }
                
                response_str = json.dumps(response)
                safe_response = dict(response)
                if safe_response.get("responseObject") and method in {"createCAdESFromBase64", "createCMSSignatureFromBase64"}:
                    safe_response["responseObject"] = f"<signed:{len(str(response['responseObject']))} chars>"
                logger.info(f"Отправка ответа: {json.dumps(safe_response, ensure_ascii=False)}")
                await websocket.send(response_str)
                
            except json.JSONDecodeError:
                logger.error("Получен невалидный JSON")
                await websocket.send(json.dumps({"code": "500", "message": "Invalid JSON"}))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Соединение закрыто: {client_ip}")
    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def main():
    host = "127.0.0.1"
    port = 13579
    
    logger.info(f"Запуск NCALayer Mock сервера на {host}:{port}...")
    
    # NCALayer локально общается без WSS или с самоподписанным сертификатом. 
    # В браузере обычно стучатся на wss://127.0.0.1:13579 или ws://127.0.0.1:13579
    # Начнем с простого ws сервера.
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # Бесконечный цикл

if __name__ == "__main__":
    asyncio.run(main())
