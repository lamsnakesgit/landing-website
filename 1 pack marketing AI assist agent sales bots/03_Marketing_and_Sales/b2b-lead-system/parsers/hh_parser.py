"""
hh.kz & hh.ru Parser — вакансии, компании, контакты
"""

import httpx
import asyncio
import argparse
import json
import re
import os
import logging
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

def extract_email(text: str) -> Optional[str]:
    if not text:
        return ""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> Optional[str]:
    if not text:
        return ""
    match = re.search(r"[\+7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    return match.group(0) if match else ""

async def parse_hh_html(domain: str, city: str, sphere: str, role: str = "", max_pages: int = 2) -> Dict:
    query = f"{role} {sphere}".strip()
    log.info(f"HH ({domain}) — запуск HTML поиска по запросу: '{query}'")

    companies = {}
    vacancies = []
    contacts = []

    area = "40" if domain == "hh.kz" else "113"
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for page in range(max_pages):
            url = f"https://{domain}/search/vacancy?text={query}&area={area}&page={page}"
            try:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    log.warning(f"HH HTML {domain} вернул статус {resp.status_code}")
                    break
                    
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.find_all('a', href=lambda h: h and '/vacancy/' in h and 'query=' in h)
                
                if not links:
                    log.info(f"На странице {page+1} {domain} вакансий не найдено.")
                    break
                    
                for l in links:
                    vac_title = l.get_text(strip=True)
                    vac_url = l.get('href').split('?')[0]
                    if not vac_url.startswith('http'):
                        vac_url = f"https://{domain}{vac_url}"
                        
                    vac_id = re.search(r"/vacancy/(\d+)", vac_url)
                    v_id = vac_id.group(1) if vac_id else vac_url
                    
                    container = l.find_parent('div', class_=re.compile(r'vacancy-card|serp-item')) or l.find_parent('div', class_=re.compile(r'template-svg|magritte')) or l.parent.parent.parent
                    
                    comp_link = container.find('a', href=lambda h: h and '/employer/' in h) if container else None
                    comp_name = comp_link.get_text(strip=True) if comp_link else f"Компания ({domain})"
                    comp_url = ""
                    if comp_link:
                        c_href = comp_link.get('href', '').split('?')[0]
                        comp_url = f"https://{domain}{c_href}" if c_href.startswith('/') else c_href
                        
                    clean_name = re.sub(r'[^a-zA-Z0-9_]+', '_', comp_name)
                    comp_id = f"hh_{clean_name}"
                    
                    snippet = ""
                    if container:
                        snippet_el = container.select_one('[class*="snippet"], [class*="responsibility"], [class*="requirement"]')
                        if snippet_el:
                            snippet = snippet_el.get_text(strip=True)
                            
                    city_el = container.select_one('[data-qa*="address"], [class*="address"]') if container else None
                    vac_city = city_el.get_text(strip=True) if city_el else city
                    
                    phone = extract_phone(snippet)
                    email = extract_email(snippet)
                    
                    if comp_id not in companies:
                        companies[comp_id] = {
                            "id": comp_id,
                            "name": comp_name,
                            "site": comp_url or vac_url,
                            "phone": phone,
                            "email": email,
                            "city": vac_city,
                            "description": snippet,
                            "category": sphere,
                            "source": domain,
                            "hh_url": vac_url,
                        }
                        
                    vacancies.append({
                        "company_id": comp_id,
                        "vacancy_id": v_id,
                        "title": vac_title,
                        "description": snippet,
                        "url": vac_url,
                        "salary": "",
                        "city": vac_city,
                        "published_at": "",
                        "source": domain,
                    })
                    
                    if phone or email:
                        contacts.append({
                            "company_id": comp_id,
                            "vacancy_id": v_id,
                            "name": "HR / Рекрутер",
                            "role": vac_title,
                            "email": email,
                            "phone": phone,
                            "contact_link": vac_url,
                            "source": domain
                        })
                        
            except Exception as e:
                log.error(f"Ошибка при скрапинге HTML HH ({domain}, стр {page}): {e}")
                break

    log.info(f"HH ({domain}) завершен. Компаний: {len(companies)}, Вакансий: {len(vacancies)}")
    return {
        "companies": list(companies.values()),
        "vacancies": vacancies,
        "contacts": contacts
    }

async def parse_hh(city: str, sphere: str, role: str, max_pages: int = 2) -> dict:
    domain = "hh.kz" if city.lower() in ["казахстан", "алматы", "астана", "шымкент"] else "hh.ru"
    return await parse_hh_html(domain, city, sphere, role, max_pages)

if __name__ == "__main__":
    res = asyncio.run(parse_hh("Алматы", "боты", ""))
    print(f"Найдено компаний: {len(res['companies'])}, вакансий: {len(res['vacancies'])}")
