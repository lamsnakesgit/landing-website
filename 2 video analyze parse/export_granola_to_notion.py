import os
import json
import urllib.request
import io
import gzip
from datetime import datetime
from dotenv import load_dotenv
import httpx
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv("notion_api_key")
NOTION_DATABASE_ID = "308467d252f1819281fbcdc52ddf29d0"
GRANOLA_CACHE_PATH = os.path.expanduser("~/Library/Application Support/Granola/cache-v6.json")
ACCOUNTS_PATH = os.path.expanduser("~/Library/Application Support/Granola/stored-accounts.json")

def get_granola_token():
    try:
        with open(ACCOUNTS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        accounts = json.loads(data['accounts'])
        tokens = json.loads(accounts[0]['tokens'])
        return tokens.get('access_token')
    except Exception as e:
        print(f"❌ Ошибка получения токена Granola: {e}")
        return None

def fetch_granola_transcript(doc_id, token):
    url = "https://api.granola.ai/v1/get-document-transcript"
    payload = json.dumps({"document_id": doc_id}).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as res:
            raw_data = res.read()
            if res.info().get('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=io.BytesIO(raw_data)) as gz:
                    data = json.loads(gz.read().decode('utf-8'))
            else:
                data = json.loads(raw_data.decode('utf-8'))
            
            transcript_text = ""
            for segment in data:
                speaker = segment.get("speaker_name") or f"Speaker {segment.get('speaker_id')}"
                text = segment.get("text", "")
                transcript_text += f"**{speaker}**: {text}\n\n"
            return transcript_text.strip()
    except Exception as e:
        print(f"⚠️ Ошибка загрузки транскрипта {doc_id}: {e}")
        return ""

def extract_tiaptap_text(node):
    text = ''
    if isinstance(node, dict):
        if node.get('type') == 'text':
            text += node.get('text', '')
        elif node.get('type') == 'heading':
            level = node.get('attrs', {}).get('level', 1)
            text += '\n' + '#' * level + ' '
        elif node.get('type') == 'paragraph':
            text += '\n'
        elif node.get('type') == 'listItem':
            text += '\n- '
        
        for k, v in node.items():
            if k not in ['type', 'text']:
                text += extract_tiaptap_text(v)
    elif isinstance(node, list):
        for item in node:
            text += extract_tiaptap_text(item)
    return text

def get_all_notes_from_cache(doc_id, title, cache_data):
    notes = {"manual": "", "ai_summary": ""}
    state = cache_data.get('cache', {}).get('state', {})
    docs = state.get('documents', {})
    
    # 1. Manual Notes (TiapTap JSON)
    doc_entry = docs.get(doc_id)
    if doc_entry and doc_entry.get('notes'):
        notes["manual"] = extract_tiaptap_text(doc_entry['notes']).strip()
    
    # 2. AI Summary (Active context)
    mchat = state.get('multiChatState', {})
    if mchat.get('chatContext', {}).get('meetingId') == doc_id:
        active_md = mchat.get('chatContext', {}).get('activeEditorMarkdown', '')
        if active_md and '###' in active_md:
            notes["ai_summary"] = active_md.strip()
            
    # 3. AI Summary (Chat message history)
    threads = state.get('entities', {}).get('chat_thread', {})
    messages = state.get('entities', {}).get('chat_message', {})
    target_thread_ids = [t_id for t_id, t_val in threads.items() if t_val.get('data', {}).get('title') == title]
    
    chat_summaries = []
    for m_id, m_val in messages.items():
        data_f = m_val.get('data', {})
        if data_f.get('thread_id') in target_thread_ids or doc_id in str(data_f):
            if data_f.get('role') == 'assistant':
                txt = data_f.get('raw_text', '')
                if not txt:
                    for out in (data_f.get('outputs') or []):
                        txt += (out.get('plain_text') or '')
                        for line in (out.get('response_lines') or []):
                            txt += line.get('answer_text', '') + '\n'
                if '### ' in txt:
                    chat_summaries.append(txt.strip())
    
    if chat_summaries:
        hist_combined = "\n\n---\n\n".join(set(chat_summaries))
        if notes["ai_summary"]:
            if hist_combined[:100] not in notes["ai_summary"]:
                notes["ai_summary"] += "\n\n" + hist_combined
        else:
            notes["ai_summary"] = hist_combined
            
    return notes

def get_notion_page(title, date_iso):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    date_only = date_iso.split('T')[0]
    payload = {"filter": {"and": [{"property": "Title", "title": {"equals": title}}, {"property": "Date", "date": {"equals": date_only}}]}}
    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                results = res.json().get("results", [])
                return results[0] if results else None
    except: pass
    return None

def create_toggle(title_text, content_text):
    if not content_text: return None
    chunks = [content_text[i:i+2000] for i in range(0, min(len(content_text), 40000), 2000)]
    children = []
    for chunk in chunks:
        children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}})
    return {
        "object": "block", "type": "toggle",
        "toggle": {"rich_text": [{"type": "text", "text": {"content": title_text}}], "children": children}
    }

def update_or_create_page(notion, db_id, title, date_str, participants, notes_data, transcript):
    existing_page = get_notion_page(title, date_str)
    
    new_blocks = []
    if transcript:
        new_blocks.append(create_toggle("📄 Full Transcript (Полная транскрипция)", transcript))
    if notes_data["manual"]:
        new_blocks.append(create_toggle("📝 Manual Notes (Ручные заметки)", notes_data["manual"]))
    if notes_data["ai_summary"]:
        new_blocks.append(create_toggle("🤖 AI Summary (ИИ Саммари/Рецепты)", notes_data["ai_summary"]))
    
    new_blocks = [b for b in new_blocks if b]

    if existing_page:
        page_id = existing_page["id"]
        # Check existing blocks to avoid duplication
        blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
        existing_toggles = []
        for b in blocks:
            if b["type"] == "toggle":
                rt = b["toggle"]["rich_text"]
                if rt: existing_toggles.append(rt[0]["text"]["content"])
        
        # Filter blocks that are already there
        blocks_to_append = []
        for nb in new_blocks:
            nb_title = nb["toggle"]["rich_text"][0]["text"]["content"]
            if nb_title not in existing_toggles:
                blocks_to_append.append(nb)
        
        if blocks_to_append:
            notion.blocks.children.append(block_id=page_id, children=blocks_to_append)
            print(f"🆙 Обновлено (добавлены блоки): {title}")
        else:
            print(f"✅ Без изменений (всё уже есть): {title}")
    else:
        # Create new page
        attendees = [{"name": p.replace(",", "")} for p in participants]
        properties = {
            "Title": {"title": [{"text": {"content": title[:2000]}}]},
            "Date": {"date": {"start": date_str}},
            "Date 1": {"date": {"start": date_str}},
            "Attendees": {"multi_select": attendees}
        }
        notion.pages.create(parent={"database_id": db_id}, properties=properties, children=new_blocks)
        print(f"🆕 Создано: {title}")

def main():
    if not NOTION_TOKEN: return print("❌ Notion Token missing")
    granola_token = get_granola_token()
    if not granola_token: return
    notion = Client(auth=NOTION_TOKEN)

    try:
        with open(GRANOLA_CACHE_PATH, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        docs = cache_data.get('cache', {}).get('state', {}).get('documents', {})
    except Exception as e: return print(f"❌ Ошибка кэша: {e}")

    target_start = datetime(2026, 2, 17)
    targets = []
    for d_id, doc in docs.items():
        if not doc: continue
        ca = doc.get("created_at")
        if not ca: continue
        try:
            dt = datetime.fromisoformat(ca.replace("Z", "+00:00")).replace(tzinfo=None)
            if dt >= target_start: targets.append((d_id, doc, ca))
        except: continue

    print(f"🎯 Найдено встреч (с 17 фев): {len(targets)}")
    for d_id, doc, date_str in targets:
        title = doc.get('title') or 'Без названия'
        notes_data = get_all_notes_from_cache(d_id, title, cache_data)
        transcript = fetch_granola_transcript(d_id, granola_token)
        
        participants = []
        p_data = doc.get('people', {})
        if p_data:
            if isinstance(p_data, dict): p_data = p_data.values()
            for p in p_data:
                if isinstance(p, dict) and 'creator' in p:
                    name = p['creator'].get('name', '')
                    if name: participants.append(name.strip())
        
        update_or_create_page(notion, NOTION_DATABASE_ID, title, date_str, participants, notes_data, transcript)

    print("🎉 Готово!")

if __name__ == "__main__":
    main()
