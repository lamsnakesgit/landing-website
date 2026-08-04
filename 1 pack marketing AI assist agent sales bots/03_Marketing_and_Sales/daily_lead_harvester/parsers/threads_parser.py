import re
import logging
from .serp_helper import search_site_leads

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_threads_leads(queries, max_per_query=5):
    """
    Парсер постов и потенциальных заказчиков с Threads.net.
    """
    leads = []

    for query in queries:
        logger.info(f"🔎 Сканируем [threads.net] по запросу: '{query}'...")
        serp_results = search_site_leads("threads.net", query, max_results=max_per_query)

        for item in serp_results:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("snippet", "")

            username_match = re.search(r'threads\.net/@([^/&?]+)', url)
            username = f"@{username_match.group(1)}" if username_match else "Автор Threads"

            contacts = f"Threads: {username} | {url}"

            leads.append({
                "source": "threads.net",
                "query": query,
                "company": f"Профиль Threads ({username})",
                "title": title or f"Пост Threads [{query}]",
                "contacts": contacts,
                "email": "",
                "phone": "",
                "contact_person": username,
                "link": url,
                "details": snippet[:250]
            })

    logger.info(f"✅ [threads.net] Завершено! Собрано лидов: {len(leads)}")
    return leads
