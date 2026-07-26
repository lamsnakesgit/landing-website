from bs4 import BeautifulSoup

def main():
    with open("scratch/hh_search_result.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(attrs={"data-qa": "vacancy-serp__vacancy"})
    if not items:
        print("No items")
        return
        
    first = items[0]
    for tag in first.find_all(True):
        data_qa = tag.get("data-qa")
        if data_qa:
            print(f"Tag: {tag.name}, data-qa: {data_qa}, Text: {tag.get_text(strip=True)[:100]}")

if __name__ == "__main__":
    main()
