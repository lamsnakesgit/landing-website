import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("notion_api_key")
DATABASE_ID = "308467d252f1819281fbcdc52ddf29d0"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def query_notion(path, method="POST", body=None):
    url = f"https://api.notion.com/v1/{path}"
    with httpx.Client(timeout=120.0) as client:
        if method == "POST":
            res = client.post(url, headers=HEADERS, json=body or {})
        elif method == "GET":
            res = client.get(url, headers=HEADERS)
        elif method == "PATCH":
            res = client.patch(url, headers=HEADERS, json=body or {})
        
        if res.status_code != 200:
            print(f"❌ API Error {res.status_code}: {res.text}")
            return None
        return res.json()

def get_page_content_info(page_id):
    try:
        res = query_notion(f"blocks/{page_id}/children", method="GET")
        if not res: return {"has_transcript": False, "has_notes": False, "block_count": 0, "blocks": []}
        
        blocks = res.get("results", [])
        has_transcript = False
        has_notes = False
        
        for b in blocks:
            if b["type"] == "toggle":
                text = "".join([t["plain_text"] for t in b["toggle"]["rich_text"]])
                if "Transcript" in text: has_transcript = True
                if "Notes" in text or "📝" in text: has_notes = True
        
        return {
            "has_transcript": has_transcript,
            "has_notes": has_notes,
            "block_count": len(blocks),
            "blocks": blocks
        }
    except:
        return {"has_transcript": False, "has_notes": False, "block_count": 0, "blocks": []}

def smart_cleanup():
    if not NOTION_TOKEN:
        print("❌ Token missing")
        return

    print("🧹 Запуск МАКСИМАЛЬНО надежной дедупликации (Direct HTTP)...")
    
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        body = {}
        if next_cursor: body["start_cursor"] = next_cursor
        
        res = query_notion(f"databases/{DATABASE_ID}/query", method="POST", body=body)
        if not res: break
        
        results = res.get("results", [])
        all_pages.extend(results)
        
        has_more = res.get("has_more", False)
        next_cursor = res.get("next_cursor")
        print(f"📡 Собрано страниц: {len(all_pages)}")

    if not all_pages:
        print("✅ База пуста.")
        return

    groups = {}
    for p in all_pages:
        try:
            props = p["properties"]
            title_list = props.get("Title", {}).get("title", []) or props.get("Название", {}).get("title", [])
            title = title_list[0]["text"]["content"] if title_list else "Untitled"
            
            date_prop = props.get("Date", {}).get("date") or props.get("Дата", {}).get("date")
            date = date_prop["start"] if date_prop else "NoDate"
            
            key = (title, date)
            if key not in groups: groups[key] = []
            groups[key].append(p)
        except: continue

    print(f"📊 Уникальных ключей: {len(groups)}")

    for (title, date), pages in groups.items():
        if len(pages) <= 1: continue
        
        print(f"🔎 Обработка {len(pages)} дублей: {title} ({date})")
        
        infos = []
        for p in pages:
            info = get_page_content_info(p["id"])
            info["page"] = p
            infos.append(info)
        
        infos.sort(key=lambda x: (x["has_transcript"] and x["has_notes"], x["block_count"]), reverse=True)
        
        winner = infos[0]
        losers = infos[1:]
        
        winner_id = winner["page"]["id"]
        print(f"🏆 Оставляем: {winner_id}")
        
        # Мерж данных
        new_blocks = []
        if not winner["has_transcript"]:
            for l in losers:
                if l["has_transcript"]:
                    for b in l["blocks"]:
                        if b["type"] == "toggle" and "Transcript" in "".join([t["plain_text"] for t in b["toggle"]["rich_text"]]):
                            new_blocks.append({"type": "toggle", "toggle": b["toggle"]})
                            winner["has_transcript"] = True
                            print("📎 Мерж транскрипта...")
                            break
        
        if not winner["has_notes"]:
            for l in losers:
                if l["has_notes"]:
                    for b in l["blocks"]:
                        text = "".join([t["plain_text"] for t in b["toggle"]["rich_text"]])
                        if "Notes" in text or "📝" in text:
                            new_blocks.append({"type": "toggle", "toggle": b["toggle"]})
                            winner["has_notes"] = True
                            print("📎 Мерж заметок...")
                            break
        
        if new_blocks:
            query_notion(f"blocks/{winner_id}/children", method="PATCH", body={"children": new_blocks})

        # Архивация дублей
        for l in losers:
            query_notion(f"pages/{l['page']['id']}", method="PATCH", body={"archived": True})
            print(f"🗑 Удален дубль {l['page']['id']}")

    print("✨ Дедупликация успешно завершена!")

if __name__ == "__main__":
    smart_cleanup()
