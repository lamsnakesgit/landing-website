import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath("scratch/granola-export/scripts"))

try:
    from api import load_workos_token, refresh_workos_token, list_all_documents, get_transcript, get_panels, pm_to_md, TokenError
    
    token = None
    try:
        token = load_workos_token()
        print("Использован существующий токен.")
    except TokenError as te:
        print("Существующий токен истек, пробуем обновить через refresh_token...")
        try:
            token = refresh_workos_token()
            print("Токен успешно обновлен!")
        except Exception as re:
            print("Не удалось обновить токен:", re)
            raise te

    docs = list_all_documents(token)
    print(f"Всего найдено встреч в аккаунте: {len(docs)}")
    
    today_str = "2026-06-03" # Текущая дата по метаданным
    today_docs = []
    
    print("\nПоследние 10 встреч:")
    for doc in docs[:10]:
        created_at = doc.get("createdAt") or doc.get("created_at") or doc.get("startTime") or ""
        doc_date = ""
        if created_at:
            doc_date = created_at.split("T")[0]
            
        print(f"- [{doc_date}] {doc.get('title') or 'Без названия'} (ID: {doc.get('id')})")
        if doc_date == today_str:
            today_docs.append(doc)
            
    print(f"\nНайдено встреч за сегодня ({today_str}): {len(today_docs)}")
    for doc in today_docs:
        print(f"\n--- Встреча: {doc.get('title')} ---")
        panels = get_panels(doc["id"], token)
        summary = pm_to_md(panels)
        print("ВЫЖИМКА:")
        print(summary[:1000] + ("..." if len(summary) > 1000 else ""))
        
except Exception as e:
    print("Ошибка при проверке Granola:", e)
