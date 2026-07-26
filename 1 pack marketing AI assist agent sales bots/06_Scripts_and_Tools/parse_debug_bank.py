from bs4 import BeautifulSoup

with open("debug_bank_ru.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, 'html.parser')
    
select = soup.find('select', {'id': 'j_idt35:j_idt40:j_idt41:edit-category'})
if select:
    opts = select.find_all('option')
    for o in opts:
        val = o.get('value')
        text = o.text.strip()
        if val and text:
            print(f"{text} (Код: {val})")
else:
    print("Не найден select")
