import requests
import json
from bs4 import BeautifulSoup

with open("sud_cookies.json", "r") as f:
    cookies = json.load(f)

s = requests.Session()
for c in cookies:
    s.cookies.set(c['name'], c['value'], domain=c['domain'])

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    # Let's try the main page first or the search page
    r = s.get("https://office.sud.kz/", headers=headers, timeout=10, verify=False)
    print("Status:", r.status_code)
    
    # Try the search endpoint
    r2 = s.get("https://office.sud.kz/lawsuit/index.xhtml", headers=headers, timeout=10, verify=False)
    print("Status Lawsuit:", r2.status_code)
    
    if r2.status_code == 200:
        soup = BeautifulSoup(r2.text, 'html.parser')
        form = soup.find('form')
        if form:
            print("Found form in Lawsuit!")
        else:
            print("No form found. Title:", soup.title.string if soup.title else "No title")
            print("Snippet:", r2.text[:200])
except Exception as e:
    print("Error:", e)
