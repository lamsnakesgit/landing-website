from bs4 import BeautifulSoup

def main():
    with open("scratch/hh_search_result.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(attrs={"data-qa": "vacancy-serp__vacancy"})
    if not items:
        print("No items found")
        return
        
    first_item = items[0]
    print("=== FIRST ITEM HTML ===")
    print(first_item.prettify()[:2000]) # Выведем первые 2000 символов красивой верстки
    
if __name__ == "__main__":
    main()
