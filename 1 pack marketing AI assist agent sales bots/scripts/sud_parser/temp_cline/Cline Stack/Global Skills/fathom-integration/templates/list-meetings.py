"""Минимальный пример чтения встреч Fathom через REST API."""

import os
import sys
from typing import Any

import httpx


BASE_URL = "https://api.fathom.ai/external/v1/meetings"
API_KEY = os.getenv("FATHOM_API_KEY")
CREATED_AFTER = os.getenv("FATHOM_CREATED_AFTER")
CREATED_BEFORE = os.getenv("FATHOM_CREATED_BEFORE")
INCLUDE_TRANSCRIPT = os.getenv("FATHOM_INCLUDE_TRANSCRIPT", "false").lower() == "true"
INCLUDE_SUMMARY = os.getenv("FATHOM_INCLUDE_SUMMARY", "false").lower() == "true"
MAX_PAGES = int(os.getenv("FATHOM_MAX_PAGES", "2"))


def build_params(cursor: str | None = None) -> dict[str, Any]:
    """Собирает query params без лишних пустых значений."""
    params: dict[str, Any] = {}
    if cursor:
        params["cursor"] = cursor
    if CREATED_AFTER:
        params["created_after"] = CREATED_AFTER
    if CREATED_BEFORE:
        params["created_before"] = CREATED_BEFORE
    if INCLUDE_TRANSCRIPT:
        params["include_transcript"] = "true"
    if INCLUDE_SUMMARY:
        params["include_summary"] = "true"
    return params


def fetch_page(client: httpx.Client, cursor: str | None = None) -> dict[str, Any]:
    """Получает одну страницу встреч из Fathom."""
    response = client.get(
        BASE_URL,
        params=build_params(cursor),
        headers={
            "X-Api-Key": API_KEY or "",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    """Печатает несколько страниц встреч и ключевые поля для дебага."""
    if not API_KEY:
        print("Нужно задать переменную окружения FATHOM_API_KEY", file=sys.stderr)
        return 1

    cursor: str | None = None

    with httpx.Client(timeout=30.0) as client:
        for page_number in range(1, MAX_PAGES + 1):
            page = fetch_page(client, cursor)
            print(f"\n=== Page {page_number} ===")
            for item in page.get("items", []):
                print(
                    {
                        "recording_id": item.get("recording_id"),
                        "title": item.get("title"),
                        "meeting_title": item.get("meeting_title"),
                        "created_at": item.get("created_at"),
                        "share_url": item.get("share_url"),
                    }
                )

            cursor = page.get("next_cursor")
            if not cursor:
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
