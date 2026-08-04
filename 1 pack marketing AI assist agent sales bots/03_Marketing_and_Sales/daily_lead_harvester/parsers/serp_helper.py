import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import logging
import time

logger = logging.getLogger(__name__)

def search_site_leads(domain, query, max_results=5):
    """
    Универсальный парсер SERP через Yahoo / DuckDuckGo HTML engine.
    Находит ссылки на компании, профили и посты по домену.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    search_query = f"site:{domain} {query}"
    encoded = urllib.parse.quote(search_query)

    # 1. Попытка через Yahoo
    url_yahoo = f"https://search.yahoo.com/search?p={encoded}"
    try:
        resp = requests.get(url_yahoo, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            result_items = soup.find_all("div", class_=lambda x: isinstance(x, str) and ("compTitle" in x or "algo" in x))

            count = 0
            for item in result_items:
                a_tag = item.find("a")
                if not a_tag:
                    continue

                raw_href = str(a_tag.get("href") or "")
                title = a_tag.text.strip()
                if not raw_href or not title:
                    continue

                clean_url = raw_href
                if "RU=" in raw_href:
                    match = re.search(r'RU=([^/&]+)', raw_href)
                    if match:
                        clean_url = urllib.parse.unquote(match.group(1))

                if domain in clean_url and "search.yahoo" not in clean_url:
                    comp_text = item.find_next_sibling("div") or item.find_parent("li")
                    snippet = comp_text.text.strip() if comp_text else title

                    leads.append({
                        "title": title,
                        "url": clean_url,
                        "snippet": snippet[:250]
                    })
                    count += 1
                    if count >= max_results:
                        break
    except Exception as e:
        logger.error(f"Ошибка SERP поиска для {domain} '{query}': {e}")

    # 2. Если результатов мало, добавляем через HTML поиска Bing
    if len(leads) < max_results:
        try:
            url_bing = f"https://www.bing.com/search?q={encoded}"
            resp_b = requests.get(url_bing, headers=headers, timeout=10)
            if resp_b.status_code == 200:
                soup_b = BeautifulSoup(resp_b.text, "html.parser")
                b_results = soup_b.find_all("li", class_="b_algo")
                for item in b_results:
                    a_tag = item.find("a")
                    if not a_tag:
                        continue
                    raw_href = str(a_tag.get("href") or "")
                    title = a_tag.text.strip()
                    if domain in raw_href and not any(l["url"] == raw_href for l in leads):
                        p_tag = item.find("p")
                        snippet = p_tag.text.strip() if p_tag else title
                        leads.append({
                            "title": title,
                            "url": raw_href,
                            "snippet": snippet[:250]
                        })
                        if len(leads) >= max_results:
                            break
        except Exception as e:
            logger.debug(f"Bing SERP fallback exception: {e}")

    return leads
