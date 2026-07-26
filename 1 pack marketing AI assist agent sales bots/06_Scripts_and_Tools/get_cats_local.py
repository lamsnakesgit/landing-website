import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

with open("sud_cookies.json", "r") as f:
    cookies_list = json.load(f)

cookies = {c["name"]: c["value"] for c in cookies_list}

resp = requests.get("https://office.sud.kz/form/courtActs/index.xhtml", headers=HEADERS, cookies=cookies, verify=False)
soup = BeautifulSoup(resp.text, 'html.parser')

select = soup.find('select', {'id': 'j_idt35:j_idt40:j_idt41:edit-category'})
if select:
    opts = select.find_all('option')
    for o in opts:
        if o.get('value'):
            print(f"{o.get('value')} | {o.text.strip()}")
else:
    print("Select not found. Session might be expired.")
