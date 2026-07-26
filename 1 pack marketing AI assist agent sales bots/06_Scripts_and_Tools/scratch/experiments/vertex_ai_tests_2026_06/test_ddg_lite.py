import httpx
from bs4 import BeautifulSoup
import sys

def search_ddg_lite(query):
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "q": f"site:threads.net {query}"
    }
    
    print(f"Searching DuckDuckGo Lite for: {data['q']}")
    try:
        resp = httpx.post(url, headers=headers, data=data, timeout=10.0)
        print(f"Status code: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # In DDG Lite, results are tables or rows. Let's see the structure:
        # Usually it has table rows or td elements with class result-link
        results = []
        
        # Let's find all search result links
        links = soup.find_all('a', class_='result-link')
        print(f"Found {len(links)} links with class 'result-link'")
        
        # If no result-link class is found, let's print some links on page
        if not links:
            all_links = soup.find_all('a')
            print(f"All links on page: {len(all_links)}")
            for l in all_links[:10]:
                print(f"  Href: {l.get('href')} | Text: {l.get_text(strip=True)}")
                
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Find snippet: usually in the next row or sibling elements
            # In DDG Lite, the snippet is in a td with class result-snippet
            # or in the next tr
            snippet = ""
            tr = link.find_parent('tr')
            if tr:
                # Next tr is usually the snippet
                next_tr = tr.find_next_sibling('tr')
                if next_tr:
                    snippet_td = next_tr.select_one('.result-snippet')
                    if snippet_td:
                        snippet = snippet_td.get_text(strip=True)
            
            if 'threads.net/@' in href:
                results.append({
                    "title": title,
                    "url": href,
                    "snippet": snippet
                })
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    q = "разработка ботов"
    if len(sys.argv) > 1:
        q = sys.argv[1]
    res = search_ddg_lite(q)
    print(f"Results: {len(res)}")
    for r in res[:5]:
        print(r)
