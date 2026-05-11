"""
2ГИС / Google Places Parser — поиск компаний по рубрике и гео
Поддерживает: 2ГИС API (Pro), Google Places API, Yandex Maps API
Запуск: python gis_parser.py --city Алматы --category "IT-компании" --provider 2gis
"""

import httpx
import asyncio
import argparse
import json
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ───────────────────────────── 2ГИС ─────────────────────────────

GIS_API = "https://catalog.api.2gis.com/3.0"

# Координаты центра городов Казахстана
CITY_COORDS = {
    "алматы": {"lat": 43.2220, "lon": 76.8512, "radius": 15000},
    "астана": {"lat": 51.1801, "lon": 71.4460, "radius": 12000},
    "шымкент": {"lat": 42.3000, "lon": 69.5900, "radius": 10000},
    "атырау": {"lat": 47.1167, "lon": 51.8833, "radius": 8000},
    "актобе": {"lat": 50.2839, "lon": 57.1669, "radius": 8000},
}


def get_city_coords(city: str) -> dict:
    return CITY_COORDS.get(city.lower(), CITY_COORDS["алматы"])


async def parse_2gis(
    city: str,
    category: str,
    api_key: str,
    max_pages: int = 5
) -> list[dict]:
    """
    2ГИС Catalog API v3 — поиск компаний по рубрике и гео-точке.
    Требует ключ от 2ГИС Pro (catalog.api.2gis.com).
    """
    coords = get_city_coords(city)
    companies = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, max_pages + 1):
            params = {
                "q": category,
                "point": f"{coords['lon']},{coords['lat']}",
                "radius": coords["radius"],
                "type": "branch",
                "page": page,
                "page_size": 50,
                "fields": "items.point,items.address,items.contact_groups,items.org,items.rubrics,items.external_content",
                "key": api_key,
            }

            try:
                resp = await client.get(f"{GIS_API}/items", params=params)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("result", {}).get("items", [])

                if not items:
                    break

                for item in items:
                    org = item.get("org", {})
                    contacts = {}
                    for group in item.get("contact_groups", []):
                        for c in group.get("contacts", []):
                            ctype = c.get("type", "")
                            cval = c.get("value", "")
                            if ctype == "phone" and not contacts.get("phone"):
                                contacts["phone"] = cval
                            elif ctype == "email" and not contacts.get("email"):
                                contacts["email"] = cval
                            elif ctype == "website" and not contacts.get("site"):
                                contacts["site"] = cval

                    rubrics = [r.get("name", "") for r in item.get("rubrics", [])]
                    ext = item.get("external_content", [])
                    logo = next((e.get("url") for e in ext if e.get("type") == "logo"), None)

                    companies.append({
                        "id": str(org.get("id", item.get("id", ""))),
                        "name": org.get("name", item.get("name", "")),
                        "site": contacts.get("site", ""),
                        "phone": contacts.get("phone", ""),
                        "email": contacts.get("email", ""),
                        "city": city,
                        "address": item.get("address", {}).get("name", ""),
                        "description": "",
                        "category": ", ".join(rubrics) if rubrics else category,
                        "source": "2gis",
                        "logo_url": logo or "",
                    })

                log.info(f"2ГИС страница {page}: {len(items)} объектов")
                await asyncio.sleep(0.5)

            except Exception as e:
                log.error(f"2ГИС ошибка страница {page}: {e}")
                break

    return companies


# ──────────────────── Google Places API ────────────────────────

GOOGLE_PLACES_API = "https://maps.googleapis.com/maps/api/place"


async def parse_google_places(
    city: str,
    category: str,
    api_key: str,
    max_results: int = 60
) -> list[dict]:
    """
    Google Places API — Text Search + Details.
    Требует Google Maps API key с включёнными Places API.
    """
    coords = get_city_coords(city)
    companies = []
    seen_ids = set()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Text Search
        params = {
            "query": f"{category} {city}",
            "location": f"{coords['lat']},{coords['lon']}",
            "radius": coords["radius"],
            "language": "ru",
            "key": api_key,
        }

        next_page_token = None
        iterations = 0

        while iterations < 3:
            if next_page_token:
                params = {"pagetoken": next_page_token, "key": api_key}
                await asyncio.sleep(2)  # Google требует паузу перед следующей страницей

            try:
                resp = await client.get(f"{GOOGLE_PLACES_API}/textsearch/json", params=params)
                resp.raise_for_status()
                data = resp.json()

                results = data.get("results", [])
                next_page_token = data.get("next_page_token")

                # Получаем детали по каждому месту
                for place in results:
                    place_id = place.get("place_id")
                    if place_id in seen_ids:
                        continue
                    seen_ids.add(place_id)

                    try:
                        detail_params = {
                            "place_id": place_id,
                            "fields": "name,formatted_phone_number,website,formatted_address,business_status,types,url",
                            "language": "ru",
                            "key": api_key,
                        }
                        detail_resp = await client.get(f"{GOOGLE_PLACES_API}/details/json", params=detail_params)
                        detail_data = detail_resp.json().get("result", {})

                        companies.append({
                            "id": place_id,
                            "name": detail_data.get("name", place.get("name", "")),
                            "site": detail_data.get("website", ""),
                            "phone": detail_data.get("formatted_phone_number", ""),
                            "email": "",
                            "city": city,
                            "address": detail_data.get("formatted_address", ""),
                            "description": "",
                            "category": category,
                            "source": "google_places",
                            "maps_url": detail_data.get("url", ""),
                        })
                        await asyncio.sleep(0.2)

                    except Exception as e:
                        log.warning(f"Google Places детали {place_id}: {e}")

                log.info(f"Google Places: +{len(results)} компаний (итого {len(companies)})")

                if not next_page_token or len(companies) >= max_results:
                    break
                iterations += 1

            except Exception as e:
                log.error(f"Google Places ошибка: {e}")
                break

    return companies


# ─────────────────────── Унифицированный вызов ─────────────────────────

async def parse_gis(
    city: str,
    category: str,
    provider: str,
    api_key: str,
    max_pages: int = 5
) -> dict:
    if provider == "2gis":
        companies = await parse_2gis(city, category, api_key, max_pages)
    elif provider == "google":
        companies = await parse_google_places(city, category, api_key, max_pages * 20)
    else:
        raise ValueError(f"Неизвестный провайдер: {provider}. Используй '2gis' или 'google'.")

    return {
        "companies": companies,
        "vacancies": [],
        "contacts": [],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2ГИС / Google Places Parser")
    parser.add_argument("--city", default="Алматы")
    parser.add_argument("--category", default="IT-компании")
    parser.add_argument("--provider", choices=["2gis", "google"], default="2gis")
    parser.add_argument("--api-key", required=True, help="API ключ провайдера")
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--output", default="gis_result.json")
    args = parser.parse_args()

    result = asyncio.run(parse_gis(args.city, args.category, args.provider, args.api_key, args.pages))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    log.info(f"Готово: {len(result['companies'])} компаний")
