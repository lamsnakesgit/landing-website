import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    r = requests.get("https://office.sud.kz/lawsuit/index.xhtml", headers=headers, timeout=10, verify=False)
    print("Status:", r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    form = soup.find('form')
    if form:
        print("Found form!")
        # Print select inputs and their options
        selects = form.find_all('select')
        for s in selects:
            print(f"Select ID: {s.get('id')}, Name: {s.get('name')}")
    else:
        print("No form found. Title:", soup.title.string if soup.title else "No title")
except Exception as e:
    print("Error:", e)
