import re

def main():
    with open("scratch/uchet_home_new.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Заменяем юникод-эскейпы вроде \u0410 на русские символы
    def decode_match(m):
        return m.group(0).encode('utf-8').decode('unicode-escape')
        
    decoded_content = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: m.group(0).encode('utf-8').decode('unicode_escape'), content)
    
    print("Decoded content length:", len(decoded_content))
    
    # Найдем все совпадения с "Введите" в декодированном файле
    matches = [m.start() for m in re.finditer(r'Введите', decoded_content)]
    print(f"Найдено совпадений с 'Введите': {len(matches)}")
    for idx, m in enumerate(matches):
        context = decoded_content[max(0, m-100):min(len(decoded_content), m+100)]
        print(f"Совпадение {idx}: ... {context} ...")
        
    # Найдем все теги <button>
    buttons = re.findall(r'<button[^>]*>.*?</button>', decoded_content, re.DOTALL)
    print(f"Всего кнопок: {len(buttons)}")
    for idx, btn in enumerate(buttons[:10]):
        # Очистим от лишних пробелов
        btn_clean = re.sub(r'\s+', ' ', btn)
        print(f"Кнопка {idx}: {btn_clean[:150]}...")

if __name__ == "__main__":
    main()
