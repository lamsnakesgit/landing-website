import os
import re
import urllib.parse
import httpx
import logging
from bs4 import BeautifulSoup
from typing import Optional, List, Dict

log = logging.getLogger(__name__)

def extract_email(text: str) -> Optional[str]:
    if not text:
        return ""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> Optional[str]:
    if not text:
        return ""
    # Matches typical Russian/Kazakh phone formats
    match = re.search(r"[\+7|8][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    return match.group(0) if match else ""

def parse_threads_username(url: str) -> str:
    match = re.search(r"threads\.net/@([a-zA-Z0-9_\.]+)", url)
    if match:
        return match.group(1)
    return ""

def search_tavily(query: str, api_key: str) -> List[Dict]:
    """Search Threads.net profiles using Tavily Search API"""
    log.info(f"Используем Tavily API для поиска в Threads.net по запросу: {query}")
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": f"site:threads.net {query}",
            "search_depth": "basic",
            "include_answer": False,
            "max_results": 15
        }
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get("results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            content = item.get("content", "")
            
            if "threads.net/@" in url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": content
                })
        return results
    except Exception as e:
        log.error(f"Ошибка при вызове Tavily API: {e}")
        return []

def search_ddg_lite(query: str) -> List[Dict]:
    """Search Threads.net profiles using DuckDuckGo Lite as fallback (no JS, highly reliable)"""
    log.info(f"Используем DuckDuckGo Lite для поиска в Threads.net по запросу: {query}")
    results = []
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "q": f"site:threads.net {query}"
    }
    try:
        resp = httpx.post(url, headers=headers, data=data, timeout=15.0)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.find_all('a', class_='result-link')
            
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Extract snippet
                snippet = ""
                tr = link.find_parent('tr')
                if tr:
                    next_tr = tr.find_next_sibling('tr')
                    if next_tr:
                        snippet_td = next_tr.select_one('.result-snippet')
                        if snippet_td:
                            snippet = snippet_td.get_text(strip=True)
                
                # Декодируем редиректы DDG
                decoded_href = urllib.parse.unquote(href)
                
                # Ищем URL Threads
                threads_url = ""
                if "threads.net/@" in decoded_href:
                    # Попробуем вытащить чистую ссылку из параметра uddg
                    match = re.search(r'uddg=(https://(?:www\.)?threads\.net/@[a-zA-Z0-9_\.]+)', decoded_href)
                    if match:
                        threads_url = match.group(1)
                    else:
                        # Если не в параметре, но threads.net/@ есть в самой ссылке
                        match_direct = re.search(r'(https://(?:www\.)?threads\.net/@[a-zA-Z0-9_\.]+)', decoded_href)
                        if match_direct:
                            threads_url = match_direct.group(1)
                
                if threads_url:
                    results.append({
                        "title": title,
                        "url": threads_url,
                        "snippet": snippet
                    })
    except Exception as e:
        log.error(f"Ошибка при поиске через DuckDuckGo Lite: {e}")
    return results

def parse_threads(query: str, max_results: int = 10) -> Dict:
    """
    Основная функция для поиска аккаунтов на threads.net по ключевому слову
    """
    log.info(f"Threads.net — поиск по запросу: '{query}'")
    
    tavily_key = os.getenv("TAVILY_API_KEY")
    raw_results = []
    
    if tavily_key:
        raw_results = search_tavily(query, tavily_key)
    
    if not raw_results:
        # Fallback to DDG Lite
        raw_results = search_ddg_lite(query)
        
    companies = []
    seen_usernames = set()
    
    for r in raw_results:
        url = r["url"]
        username = parse_threads_username(url)
        if not username or username in seen_usernames:
            continue
        seen_usernames.add(username)
        
        title = r["title"]
        # Clean title
        name = title.split("(@")[0].strip()
        if not name:
            name = username
            
        snippet = r["snippet"]
        email = extract_email(snippet)
        phone = extract_phone(snippet)
        
        companies.append({
            "id": f"threads_{username}",
            "name": name,
            "site": f"https://www.threads.net/@{username}",
            "phone": phone,
            "email": email,
            "city": "Удалённо / СНГ",
            "description": snippet,
            "category": f"Threads Profile: {query}",
            "source": "threads.net",
            "hh_url": f"https://www.threads.net/@{username}",
        })
        
    log.info(f"Threads.net поиск завершен. Найдено уникальных профилей: {len(companies)}")
    return {
        "companies": companies,
        "vacancies": [],
        "contacts": []
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    q = "маркетинг"
    if len(sys.argv) > 1:
        q = sys.argv[1]
    res = parse_threads(q)
    print(res)
