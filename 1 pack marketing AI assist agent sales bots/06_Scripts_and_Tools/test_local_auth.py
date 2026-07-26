import requests
import json
import urllib3
urllib3.disable_warnings()

try:
    with open('/tmp/sud_cookies.json', 'r') as f:
        cookies_list = json.load(f)
except Exception as e:
    print('Failed to load cookies:', e)
    exit(1)

session = requests.Session()
for c in cookies_list:
    session.cookies.set(c['name'], c['value'], domain=c['domain'])

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

resp = session.get('https://office.sud.kz/index.xhtml', headers=headers, verify=False, timeout=15)
html = resp.text

if 'logout' in html or 'Шығу' in html or 'Выйти' in html:
    print('SUCCESS! WE ARE LOGGED IN LOCALLY!')
else:
    print('FAILED. STILL A GUEST LOCALLY.')
