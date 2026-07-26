import time
import json
import re
from playwright.sync_api import sync_playwright

def parse_uchet_niches(niches, limit_per_niche=10):
    leads = []
    
    with sync_playwright() as p:
        # ЗАПУСКАЕМ В ОТКРЫТУЮ
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for keyword in niches:
            print(f"\nðŸ”„ Ищем нишу: '{keyword}' на pk.uchet.kz...")
            try:
                page.goto("https://pk.uchet.kz/search/", timeout=60000)
                time.sleep(2)
                
                search_input = page.locator('input').first
                search_input.fill(keyword)
                search_input.press('Enter')
                time.sleep(5)
                
                # ПАРСИМ БИНы
                text_content = page.content()
                bins = re.findall(r'(?:БИН|ИИН):\s*(\d{12})', text_content)
                
                # Удаляем дубликаты
                bins = list(dict.fromkeys(bins))
                
                print(f"✅ Найдено БИН/ИИН: {len(bins)}. Идем внутрь...")
                
                for bin_number in bins[:limit_per_niche]:
                    url = f"https://pk.uchet.kz/search/bin/{bin_number}"
                    try:
                        page.goto(url, timeout=30000)
                        time.sleep(2)
                        
                        name = page.locator('h1').inner_text() if page.locator('h1').count() > 0 else "Неизвестно"
                        
                        lpr = "Не найдено"
                        blocks = page.locator('div').all()
                        for b in blocks:
                            try:
                                text = b.inner_text()
                                if 'Руководитель' in text or 'Первый руководитель' in text:
                                    lines = text.split('\n')
                                    for i, line in enumerate(lines):
                                        if 'Руководитель' in line or 'Первый руководитель' in line:
                                            if i + 1 < len(lines):
                                                lpr = lines[i+1].strip()
                                                break
                            except: pass
                            
                        phone = "Не указан"
                        phone_els = page.locator('a[href^="tel:"]').all()
                        if phone_els:
                            phone = phone_els[0].inner_text().strip()
                            
                        if phone != "Не указан":
                            print(f"ðŸ ¢ {name} | ðŸ‘¤ {lpr} | ðŸ“ž {phone}")
                            leads.append({
                                "niche": keyword,
                                "company": name,
                                "lpr": lpr,
                                "phone": phone,
                                "url": url
                            })
                    except Exception as ex:
                        pass
                        
            except Exception as e:
                print(f"❌ Ошибка в нише {keyword}: {e}")
                
        try: browser.close()
        except: pass
            
    with open("uchet_mac_leads.json", "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print(f"\nðŸŽ‰ Собрано {len(leads)} лидов. Файл: uchet_mac_leads.json")

if __name__ == "__main__":
    niches = ["ресторан", "строительная компания", "логистика", "мебель"]
    parse_uchet_niches(niches, limit_per_niche=10)
