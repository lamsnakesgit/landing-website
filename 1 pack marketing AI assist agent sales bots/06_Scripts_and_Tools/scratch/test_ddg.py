import httpx
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Попробуем GET-запрос к HTML-версии DuckDuckGo (html.duckduckgo.com или lite.duckduckgo.com)
url = "https://html.duckduckgo.com/html/"
params = {"q": "site:threads.net боты"}

try:
    r = httpx.get(url, params=params, headers=headers, timeout=10.0)
    print("HTML Version Status:", r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.select('a.result__url')
    print("Found links on HTML version:", len(links))
    for i, a in enumerate(links[:5]):
        print(f"[{i+1}] {a.get_text(strip=True)} -> {a.get('href')}")
except Exception as e:
    print("HTML Version failed:", e)

# Попробуем lite-версию
url_lite = "https://lite.duckduckgo.com/lite/"
data = {"q": "site:threads.net боты"}
try:
    r = httpx.post(url_lite, data=data, headers=headers, timeout=10.0)
    print("Lite Version Status:", r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    # В lite-версии ссылки обычно находятся в таблице. Давайте поищем все ссылки с href, содержащим threads.net
    links = soup.find_all('a')
    ddg_links = [a for a in links if a.get('href') and ('threads.net' in a.get('href') or 'uddg' in a.get('href'))]
    print("Found links on Lite version:", len(ddg_links))
    for i, a in enumerate(ddg_links[:5]):
        print(f"[{i+1}] {a.get_text(strip=True)} -> {a.get('href')}")
except Exception as e:
    print("Lite Version failed:", e)
