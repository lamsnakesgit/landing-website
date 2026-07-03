import requests
import json
import re
from bs4 import BeautifulSoup
from auth_kalkan import auth_kalkan_with_retry

BASE_URL = "https://office.sud.kz"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

def search_global_cases(session: requests.Session):
    print("🔍 Открываем Банк судебных актов...")
    resp = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)
    
    # Ищем ViewState
    view_state_match = re.search(r'id="j_id1:javax.faces.ViewState:\d+"\s+value="([^"]+)"', resp.text)
    if not view_state_match:
        print("❌ Не найден ViewState для поиска")
        return
    view_state = view_state_match.group(1)
    
    # Трудовые споры ID
    category_id = "142030000100000000"
    print(f"📡 Отправляем запрос на поиск (Трудовые споры: {category_id})...")
    
    ajax_headers = HEADERS.copy()
    ajax_headers["Faces-Request"] = "partial/ajax"
    ajax_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    
    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt35:j_idt40:j_idt41:j_idt135",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "@all",
        "j_idt35:j_idt40:j_idt41:j_idt135": "j_idt35:j_idt40:j_idt41:j_idt135",
        "j_idt35:j_idt40:j_idt41": "j_idt35:j_idt40:j_idt41",
        "j_idt35:j_idt40:j_idt41:edit-category": category_id,
        "javax.faces.ViewState": view_state
    }
    
    resp_search = session.post(f"{BASE_URL}/form/courtActs/index.xhtml", headers=ajax_headers, data=data)
    
    with open("/output/search_results.xml", "w") as f:
        f.write(resp_search.text)
        
    print(f"✅ Поиск выполнен. Размер ответа: {len(resp_search.text)} байт.")

    # Парсим результаты
    cases = []
    soup = BeautifulSoup(resp_search.text, "xml") # response is partial ajax XML
    
    # Извлечем весь CDATA HTML внутри <update id="j_idt35:j_idt40:j_idt41">
    # или просто найдем все таблицы в CDATA. 
    # Но проще всего заново перепарсить весь текст как HTML
    html_soup = BeautifulSoup(resp_search.text, "html.parser")
    rows = html_soup.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 3:
            clean_cells = [c.get_text(strip=True) for c in cells]
            if any("Медиация" in c for c in clean_cells):
                continue
            links = []
            for a in row.find_all('a', href=True):
                links.append({"text": a.get_text(strip=True), "href": a['href']})
            
            if any(clean_cells):
                cases.append({"data": clean_cells, "links": links})
                
    print(f"📊 Найдено дел: {len(cases)}")
    with open("/output/labor_cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    session = requests.Session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    
    if auth_kalkan_with_retry(session):
        search_global_cases(session)
    else:
        print("❌ Авторизация не удалась.")
