import time
import json
from playwright.sync_api import sync_playwright

def parse_uchet_niches(niches, limit_per_niche=10):
    leads = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
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
                
                # Get all "Открыть карточку" buttons
                buttons = page.locator('text="Открыть карточку"').all()
                links = []
                for btn in buttons:
                    # Sometimes it's an <a> tag
                    href = btn.get_attribute('href')
                    if href:
                        links.append(f"https://pk.uchet.kz{href}" if href.startswith('/') else href)
                        
                print(f"✅ Найдено карточек: {len(links)}. Идем внутрь...")
                
                for url in links[:limit_per_niche]:
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
