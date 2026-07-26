import requests
import urllib3
urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get('https://office.sud.kz/forum/forum.xhtml', headers=headers, verify=False, allow_redirects=False)
print("Forum:", resp.status_code)
resp2 = requests.get('https://office.sud.kz/legitimacy/index.xhtml', headers=headers, verify=False, allow_redirects=False)
print("Legitimacy:", resp2.status_code)
resp3 = requests.get('https://office.sud.kz/scheduleOfCases/index.xhtml', headers=headers, verify=False, allow_redirects=False)
print("Schedule:", resp3.status_code)
resp4 = requests.get('https://office.sud.kz/lawsuit/index.xhtml', headers=headers, verify=False, allow_redirects=False)
print("Lawsuit:", resp4.status_code)
