import json
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def parse_threads_leads(keyword: str, max_results: int = 10) -> str:
    """
    Выполняет поиск профилей и постов в Threads по заданному ключевому слову,
    отфильтровывая результаты, похожие на лиды.
    """
    logger.info(f"Начинаю поиск лидов в Threads по запросу: {keyword}")
    
    query = f"site:threads.net {keyword} (email OR contact OR dm OR @)"
    
    leads = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            for res in results:
                url = res.get('href', '')
                title = res.get('title', '')
                snippet = res.get('body', '')
                
                # Фильтруем только профили и посты Threads
                if 'threads.net' in url:
                    leads.append({
                        "profile_url": url,
                        "title": title,
                        "bio_or_post_snippet": snippet
                    })
                    
        if not leads:
            return json.dumps({"status": "no_leads_found", "keyword": keyword}, ensure_ascii=False)
            
        return json.dumps({
            "status": "success",
            "keyword": keyword,
            "leads_found": len(leads),
            "leads": leads
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Ошибка парсинга Threads: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

if __name__ == "__main__":
    # Тест
    print(parse_threads_leads("AI маркетолог"))
