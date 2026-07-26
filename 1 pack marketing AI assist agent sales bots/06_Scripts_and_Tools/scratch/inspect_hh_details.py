from bs4 import BeautifulSoup

def main():
    with open("scratch/hh_search_result.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(attrs={"data-qa": "vacancy-serp__vacancy"})
    if not items:
        print("No items found")
        return
        
    for idx, item in enumerate(items[:3]):
        print(f"\n--- ITEM {idx+1} ---")
        
        # Название и ссылка
        title_el = item.find(attrs={"data-qa": "serp-item__title"})
        title = title_el.get_text(strip=True) if title_el else "None"
        href = title_el.get("href") if title_el else "None"
        
        # Компания
        company_el = item.find(attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        company = company_el.get_text(strip=True) if company_el else "None"
        company_href = company_el.get("href") if company_el else "None"
        
        # Зарплата
        # Обычно имеет data-qa="vacancy-serp__vacancy-compensation" или лежит в magritte-text с определенными стилями
        salary_el = item.find(attrs={"data-qa": "vacancy-serp__vacancy-compensation"})
        if not salary_el:
            # Попробуем поискать по тексту или другим классам
            salary_el = item.select_one("[class*='compensation'], [class*='salary']")
        salary = salary_el.get_text(strip=True) if salary_el else "Не указана"
        
        # Город
        city_el = item.find(attrs={"data-qa": "vacancy-serp__vacancy-address"})
        city = city_el.get_text(strip=True) if city_el else "None"
        
        # Описание / Сниппет
        snippet_el = item.find(attrs={"data-qa": "vacancy-serp__vacancy_snippet_responsibility"})
        snippet_resp = snippet_el.get_text(strip=True) if snippet_el else ""
        
        snippet_req_el = item.find(attrs={"data-qa": "vacancy-serp__vacancy_snippet_requirement"})
        snippet_req = snippet_req_el.get_text(strip=True) if snippet_req_el else ""
        
        description = f"{snippet_resp} {snippet_req}".strip()
        
        print(f"Title: {title}")
        print(f"Link: {href}")
        print(f"Company: {company} ({company_href})")
        print(f"Salary: {salary}")
        print(f"City: {city}")
        print(f"Desc: {description[:100]}...")

if __name__ == "__main__":
    main()
