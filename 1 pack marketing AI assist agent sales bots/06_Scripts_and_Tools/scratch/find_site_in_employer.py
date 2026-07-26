from bs4 import BeautifulSoup
import re

def main():
    with open("scratch/employer_detail.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Выведем все ссылки, которые ведут не на hh.ru
    print("=== EXTERNAL LINKS ===")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if not href.startswith("/") and "hh.ru" not in href and "hh.kz" not in href:
            print(f"Href: {href}, Text: {text}, attrs: {a.attrs}")

if __name__ == "__main__":
    main()
