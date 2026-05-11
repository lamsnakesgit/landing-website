import os
import time
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("notion_api_key")
DATABASE_ID = "308467d252f1819281fbcdc52ddf29d0"

def cleanup():
    if not NOTION_TOKEN:
        print("❌ AI Token missing")
        return

    notion = Client(auth=NOTION_TOKEN)
    print(f"🧹 Очистка базы через SEARCH: {DATABASE_ID}")
    
    # Регуляризируем ID (убираем дефисы для сравнения)
    clean_db_id = DATABASE_ID.replace("-", "")
    
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        try:
            query_kwargs = {
                "filter": {"value": "page", "property": "object"},
                "sort": {"direction": "descending", "timestamp": "last_edited_time"}
            }
            if next_cursor:
                query_kwargs["start_cursor"] = next_cursor
            
            response = notion.search(**query_kwargs)
            results = response.get("results", [])
            
            # Фильтруем страницы, которые принадлежат нашей базе
            for page in results:
                parent = page.get("parent", {})
                p_db_id = parent.get("database_id", "").replace("-", "")
                if p_db_id == clean_db_id:
                    all_pages.append(page)
            
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")
            print(f"📡 Поиск в процессе... Найдено в базе: {len(all_pages)}")
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            break

    if not all_pages:
        print("✅ База пуста (или страницы не индексированы поиском).")
        return

    print(f"🗑 Удаление {len(all_pages)} страниц...")
    for page in all_pages:
        try:
            notion.pages.update(page_id=page["id"], archived=True)
            print(f"🗑 Архив: {page['id']}")
        except: pass
    
    print("✨ Очистка завершена.")

if __name__ == "__main__":
    cleanup()
