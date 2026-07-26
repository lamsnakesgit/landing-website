import requests
import re
from bs4 import BeautifulSoup
import html as html_lib

BASE_URL = "https://office.sud.kz"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def main():
    session = requests.Session()
    session.verify = False
    import urllib3
    urllib3.disable_warnings()

    # Попробуем без авторизации открыть index Банка Актов (иногда он открывается на чтение)
    resp = session.get(f"{BASE_URL}/form/courtActs/index.xhtml", headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Ищем select или span/div с категориями
    select = soup.find('select', {'id': 'j_idt35:j_idt40:j_idt41:edit-category'})
    if not select:
        select = soup.find('select', {'id': re.compile(r'edit-category$')})
        
    if select:
        options = select.find_all('option')
        for opt in options:
            val = opt.get('value', '')
            text = opt.text.strip()
            if val and text:
                print(f"{val} | {text}")
        return

    # Если мы тут, значит страница перекинула на логин или не отдала select
    print("Не удалось получить категории. Нужно сделать ЭЦП авторизацию или сайт лежит.")
    print("HTML TITLE:", soup.title.text if soup.title else "No title")

if __name__ == "__main__":
    main()
