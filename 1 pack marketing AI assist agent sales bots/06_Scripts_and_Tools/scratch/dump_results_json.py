import time
import json
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto("https://pk.uchet.kz/", wait_until="networkidle")
        time.sleep(3)
        
        search_btn = page.locator("button[aria-label='Открыть поиск контрагента']").first
        if search_btn.count() > 0:
            page.evaluate("btn => btn.click()", search_btn.element_handle())
            time.sleep(2)
            
            label = page.locator("label:has-text('Введите ИИН')").first
            if label.count() > 0:
                parent = label.locator("..")
                inp = parent.locator("input").first
                if inp.count() > 0:
                    inp.fill("Казахтелеком")
                    time.sleep(1)
                    inp.press("Enter")
                    time.sleep(5)
                    
                    # Парсим карточки компаний с результатов
                    # Каждая карточка представляет собой тег article
                    articles = page.locator("article")
                    cnt = articles.count()
                    print(f"[*] Найдено карточек (article): {cnt}")
                    
                    results = []
                    for i in range(cnt):
                        art = articles.nth(i)
                        
                        # Извлекаем название (обычно h2)
                        name_el = art.locator("h2")
                        name = name_el.inner_text().strip() if name_el.count() > 0 else ""
                        
                        # Извлекаем весь текст внутри article
                        text = art.inner_text()
                        
                        # Парсим БИН
                        bin_val = ""
                        for line in text.split("\n"):
                            if "БИН:" in line:
                                bin_val = line.replace("БИН:", "").strip()
                                
                        # Парсим статус
                        status = ""
                        for line in text.split("\n"):
                            if "Статус:" in line:
                                status = line.replace("Статус:", "").strip()
                                
                        # Парсим Руководитель
                        rukovoditel = ""
                        lines = text.split("\n")
                        for idx, line in enumerate(lines):
                            if "Руководитель:" in line:
                                if idx + 1 < len(lines):
                                    rukovoditel = lines[idx+1].strip()
                                else:
                                    rukovoditel = line.replace("Руководитель:", "").strip()
                                    
                        # Парсим Юридический адрес
                        address = ""
                        for idx, line in enumerate(lines):
                            if "Юридический адрес:" in line:
                                # Адрес обычно идет на следующей строке
                                addr_parts = []
                                curr = idx + 1
                                while curr < len(lines) and lines[curr].strip() and not any(k in lines[curr] for k in ["БИН:", "Статус:", "Руководитель:", "Открыть карточку"]):
                                    addr_parts.append(lines[curr].strip())
                                    curr += 1
                                address = " ".join(addr_parts)
                                
                        results.append({
                            "name": name,
                            "bin": bin_val,
                            "status": status,
                            "rukovoditel": rukovoditel,
                            "address": address
                        })
                        
                    print(json.dumps(results[:5], indent=2, ensure_ascii=False))
                    
                    # Сохраняем весь список в JSON
                    with open("scratch/uchet_results.json", "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print("[+] Результаты сохранены в scratch/uchet_results.json")
                    
        browser.close()

if __name__ == "__main__":
    main()
