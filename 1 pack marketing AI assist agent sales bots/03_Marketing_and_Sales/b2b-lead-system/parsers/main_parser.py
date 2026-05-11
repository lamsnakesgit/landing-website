"""
Главный координатор парсеров — запускает все источники и сохраняет в Supabase.
Используется как HTTP endpoint (FastAPI) или напрямую из CLI.

CLI:
  python main_parser.py --city Алматы --sphere IT --role директор --sources hh,adata

HTTP (запустить сервер):
  uvicorn main_parser:app --host 0.0.0.0 --port 8080
"""

import asyncio
import argparse
import json
import logging
import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Импорт парсеров
from hh_parser import parse_hh
from adata_parser import search_adata
from gis_parser import parse_gis

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ─────────────── Конфиг Supabase ───────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_ANON_OR_SERVICE_KEY")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",  # upsert по conflict
}


# ─────────────── Supabase Writer ───────────────
async def upsert_companies(companies: list[dict]) -> int:
    if not companies:
        return 0
    mapped = []
    for c in companies:
        mapped.append({
            "external_id": str(c.get("id", "")),
            "name": c.get("name", ""),
            "site": c.get("site", ""),
            "phone": c.get("phone", ""),
            "email": c.get("email", ""),
            "city": c.get("city", ""),
            "description": c.get("description", "")[:500],
            "category": c.get("category", ""),
            "source": c.get("source", ""),
            "hh_url": c.get("hh_url", "") or c.get("maps_url", ""),
        })
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/companies",
            headers=SUPABASE_HEADERS,
            json=mapped,
        )
        if resp.status_code not in (200, 201, 204):
            log.error(f"Supabase companies error: {resp.status_code} {resp.text[:200]}")
        return len(mapped)


async def upsert_vacancies(vacancies: list[dict]) -> int:
    if not vacancies:
        return 0
    mapped = []
    for v in vacancies:
        mapped.append({
            "external_id": str(v.get("vacancy_id", "")),
            "company_external_id": str(v.get("company_id", "")),
            "title": v.get("title", ""),
            "description": v.get("description", "")[:1000],
            "url": v.get("url", ""),
            "salary": v.get("salary", ""),
            "city": v.get("city", ""),
            "published_at": v.get("published_at") or None,
            "experience": v.get("experience", ""),
            "source": v.get("source", ""),
        })
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/vacancies",
            headers=SUPABASE_HEADERS,
            json=mapped,
        )
        if resp.status_code not in (200, 201, 204):
            log.error(f"Supabase vacancies error: {resp.status_code} {resp.text[:200]}")
        return len(mapped)


async def upsert_contacts(contacts: list[dict]) -> int:
    if not contacts:
        return 0
    mapped = []
    for c in contacts:
        mapped.append({
            "company_external_id": str(c.get("company_id", "")),
            "vacancy_external_id": str(c.get("vacancy_id", "")),
            "name": c.get("name", ""),
            "role": c.get("role", ""),
            "email": c.get("email", ""),
            "phone": c.get("phone", ""),
            "contact_link": c.get("contact_link", ""),
            "source": c.get("source", ""),
        })
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/contacts",
            headers=SUPABASE_HEADERS,
            json=mapped,
        )
        if resp.status_code not in (200, 201, 204):
            log.error(f"Supabase contacts error: {resp.status_code} {resp.text[:200]}")
        return len(mapped)


# ─────────────── Главная функция ───────────────
async def run_parser(
    city: str = "Алматы",
    sphere: str = "IT",
    role: str = "директор",
    sources: list[str] = None,
    min_contacts: bool = False,
    save_to_supabase: bool = True,
    gis_api_key: str = "",
    gis_provider: str = "2gis",
    hh_pages: int = 5,
    adata_pages: int = 3,
) -> dict:
    if sources is None:
        sources = ["hh", "adata"]

    all_companies = []
    all_vacancies = []
    all_contacts = []

    tasks = []
    if "hh" in sources:
        tasks.append(("hh", parse_hh(city, sphere, role, hh_pages)))
    if "adata" in sources:
        tasks.append(("adata", search_adata(city, sphere, role, adata_pages)))
    if "2gis" in sources or "google" in sources:
        provider = "2gis" if "2gis" in sources else "google"
        if gis_api_key:
            tasks.append(("gis", parse_gis(city, sphere, gis_provider or provider, gis_api_key)))
        else:
            log.warning("2ГИС/Google: пропускаем, не указан api_key (gis_api_key)")

    results = await asyncio.gather(*[t for _, t in tasks], return_exceptions=True)

    for (src_name, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            log.error(f"Источник {src_name} ошибка: {result}")
            continue
        all_companies.extend(result.get("companies", []))
        all_vacancies.extend(result.get("vacancies", []))
        all_contacts.extend(result.get("contacts", []))

    # Фильтр: только компании с контактами (если min_contacts=True)
    if min_contacts:
        company_ids_with_contacts = {c.get("company_id") for c in all_contacts if c.get("email") or c.get("phone")}
        all_companies = [
            c for c in all_companies
            if c.get("id") in company_ids_with_contacts
            or c.get("email")
            or c.get("phone")
        ]

    # Дедупликация по имени компании
    seen_names = set()
    unique_companies = []
    for c in all_companies:
        key = c.get("name", "").lower().strip()
        if key and key not in seen_names:
            seen_names.add(key)
            unique_companies.append(c)

    stats = {
        "companies": len(unique_companies),
        "vacancies": len(all_vacancies),
        "contacts": len(all_contacts),
    }

    if save_to_supabase:
        log.info("Сохраняем в Supabase...")
        await asyncio.gather(
            upsert_companies(unique_companies),
            upsert_vacancies(all_vacancies),
            upsert_contacts(all_contacts),
        )
        log.info(f"Supabase: записано {stats}")

    return {
        "stats": stats,
        "companies": unique_companies,
        "vacancies": all_vacancies,
        "contacts": all_contacts,
    }


# ─────────────── FastAPI HTTP endpoint ───────────────
app = FastAPI(title="B2B Lead Parser API", version="1.0")


class ParseRequest(BaseModel):
    city: str = "Алматы"
    sphere: str = "IT"
    role: str = "директор"
    sources: list[str] = ["hh", "adata"]
    min_contacts: bool = False
    save_to_supabase: bool = True
    gis_api_key: str = ""
    gis_provider: str = "2gis"
    hh_pages: int = 3
    adata_pages: int = 2


@app.post("/parse")
async def parse_endpoint(req: ParseRequest):
    """
    n8n вызывает этот endpoint через HTTP Request node.
    Пример body:
    {
      "city": "Алматы",
      "sphere": "маркетинг",
      "role": "руководитель отдела",
      "sources": ["hh", "adata"],
      "save_to_supabase": true
    }
    """
    try:
        result = await run_parser(
            city=req.city,
            sphere=req.sphere,
            role=req.role,
            sources=req.sources,
            min_contacts=req.min_contacts,
            save_to_supabase=req.save_to_supabase,
            gis_api_key=req.gis_api_key,
            gis_provider=req.gis_provider,
            hh_pages=req.hh_pages,
            adata_pages=req.adata_pages,
        )
        return {"status": "ok", **result["stats"]}
    except Exception as e:
        log.exception("parse_endpoint error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


# ─────────────── CLI ───────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Алматы")
    parser.add_argument("--sphere", default="IT")
    parser.add_argument("--role", default="директор")
    parser.add_argument("--sources", default="hh,adata", help="Через запятую: hh,adata,2gis,google")
    parser.add_argument("--no-supabase", action="store_true")
    parser.add_argument("--min-contacts", action="store_true")
    parser.add_argument("--gis-api-key", default="")
    parser.add_argument("--output", default="result.json")
    args = parser.parse_args()

    sources_list = [s.strip() for s in args.sources.split(",")]

    result = asyncio.run(run_parser(
        city=args.city,
        sphere=args.sphere,
        role=args.role,
        sources=sources_list,
        min_contacts=args.min_contacts,
        save_to_supabase=not args.no_supabase,
        gis_api_key=args.gis_api_key,
    ))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    s = result["stats"]
    print(f"\n✓ Компаний: {s['companies']} | Вакансий: {s['vacancies']} | Контактов: {s['contacts']}")
    print(f"✓ Результат сохранён в {args.output}")
