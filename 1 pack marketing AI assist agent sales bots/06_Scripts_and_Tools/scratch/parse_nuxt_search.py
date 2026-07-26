import httpx
from bs4 import BeautifulSoup
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

url = "https://pk.adata.kz/search?query=разработка"
r = httpx.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NUXT_DATA__')

if script:
    data = json.loads(script.get_text())
    print("Total items in NUXT_DATA:", len(data))
    
    # Запишем NUXT_DATA в файл для детального анализа
    with open("scratch/nuxt_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # Попробуем найти БИН-ы (12 цифр) и названия ТОО/ИП в массиве
    for idx, item in enumerate(data):
        if isinstance(item, str):
            if re.match(r'^\d{12}$', item):
                print(f"Index {idx}: BIN {item}")
                # Посмотрим соседние элементы
                context = data[max(0, idx-5):min(len(data), idx+15)]
                print("  Context:", context)
else:
    print("__NUXT_DATA__ script not found!")
