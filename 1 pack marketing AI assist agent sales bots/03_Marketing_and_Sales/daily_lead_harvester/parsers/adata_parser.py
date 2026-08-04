import re
import logging
from .serp_helper import search_site_leads

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_adata_leads(queries, max_per_query=5):
    """
    Парсер казахстанских компаний с Adata.kz / pk.adata.kz.
    Собирает юрлица, ИИН/БИН и сферы работы.
    """
    leads = []

    for query in queries:
        logger.info(f"🔎 Сканируем [adata.kz] по запросу: '{query}'...")
        serp_results = search_site_leads("adata.kz", query, max_results=max_per_query)

        for item in serp_results:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("snippet", "")

            company_name = title.replace(" - Adata.kz", "").replace(" - uchet.kz", "").replace("Adata.kz", "").strip()
            if not company_name:
                company_name = f"Казахстанское ТОО/ИП ({query})"

            bin_match = re.search(r'\b\d{12}\b', snippet)
            bin_code = bin_match.group(0) if bin_match else "Казахстан"

            leads.append({
                "source": "adata.kz",
                "query": query,
                "company": company_name,
                "title": f"Контрагент: {company_name}",
                "contacts": f"Adata: {url} | БИН: {bin_code}",
                "email": "",
                "phone": "",
                "contact_person": "Руководитель компании",
                "link": url,
                "details": f"Сфера {query}: {snippet[:250]}"
            })

    logger.info(f"✅ [adata.kz] Завершено! Собрано лидов: {len(leads)}")
    return leads
