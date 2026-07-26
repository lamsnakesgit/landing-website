#!/usr/bin/env python3
"""
Анализ лида — извлечение структурированных данных с сайта компании.
Используется в pipeline sales-team для автоматического сбора метаданных.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# Детекция типа компании по сигналам на сайте
COMPANY_TYPE_SIGNALS = {
    "SaaS": [
        "free trial", "pricing", "api", "integrations", "dashboard",
        "login", "sign up", "subscription", "saas", "cloud"
    ],
    "Agency": [
        "case study", "portfolio", "clients", "testimonial",
        "work with us", "services", "retainer", "hourly"
    ],
    "E-commerce": [
        "shop", "cart", "checkout", "product", "buy",
        "shipping", "order", "reviews", "store"
    ],
    "Enterprise": [
        "enterprise", "compliance", "security", "procurement",
        "partner", "vendor", "soc2", "gdpr", "iso"
    ],
    "Startup": [
        "backed by", "seed", "series a", "yc", "accelerator",
        "beta", "early access", "founded", "mission"
    ],
    "SMB": [
        "small business", "local", "family", "owner",
        "affordable", "simple", "easy"
    ],
}


def extract_social_links(html_content):
    """Извлечение ссылок на соцсети"""
    social_patterns = {
        "linkedin": r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[^\s\"'<>]+",
        "twitter": r"https?://(?:www\.)?(?:twitter|x\.com)/[^\s\"'<>]+",
        "facebook": r"https?://(?:www\.)?facebook\.com/[^\s\"'<>]+",
        "instagram": r"https?://(?:www\.)?instagram\.com/[^\s\"'<>]+",
        "github": r"https?://(?:www\.)?github\.com/[^\s\"'<>]+",
        "telegram": r"https?://(?:t\.me|telegram\.me)/[^\s\"'<>]+",
    }
    found = {}
    for platform, pattern in social_patterns.items():
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            found[platform] = list(set(matches))[:3]
    return found


def detect_company_type(text):
    """Детекция типа компании"""
    text_lower = text.lower()
    scores = {}
    for company_type, signals in COMPANY_TYPE_SIGNALS.items():
        score = sum(1 for s in signals if s in text_lower)
        if score > 0:
            scores[company_type] = score

    if not scores:
        return "Unknown"
    return max(scores, key=scores.get)


def extract_emails(text):
    """Извлечение email-адресов"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    # Фильтруем служебные
    filtered = [e for e in emails if not any(x in e.lower() for x in ['@example', '@test', '@sentry', '@wix', '@google'])]
    return list(set(filtered))[:5]


def extract_phones(text):
    """Извлечение телефонов"""
    patterns = [
        r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}',
        r'\+[0-9]{1,3}[-\s]?[0-9]{3,}[-\s]?[0-9]{3,}[-\s]?[0-9]{0,4}',
    ]
    phones = []
    for p in patterns:
        phones.extend(re.findall(p, text))
    # Фильтруем короткие
    return [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 7][:3]


def detect_tech_stack(html_content):
    """Детекция технологического стека"""
    tech_signals = {
        "React": ["react", "_next", "next.js", "reactdom"],
        "Vue": ["vue.js", "vuejs", "_nuxt", "nuxt"],
        "Angular": ["angular", "ng-", "angularjs"],
        "WordPress": ["wp-content", "wordpress", "wp-json"],
        "Shopify": ["shopify", "cdn.shopify.com"],
        "HubSpot": ["hubspot", "hs-scripts", "hs-analytics"],
        "Salesforce": ["salesforce", "force.com", "sfcrm"],
        "Google Analytics": ["google-analytics", "gtag", "ga.js", "analytics.js"],
        "Segment": ["segment.com", "analytics.js"],
        "Intercom": ["intercom", "intercomcdn"],
        "Zendesk": ["zendesk", "zdassets.com"],
        "Stripe": ["stripe.com", "js.stripe.com"],
        "Cloudflare": ["cloudflare", "cf-ray", "cf-cache"],
        "Vercel": ["vercel", "_vercel"],
        "Netlify": ["netlify"],
        "AWS": ["amazonaws.com", "aws"],
    }
    html_lower = html_content.lower()
    found = []
    for tech, signals in tech_signals.items():
        if any(s in html_lower for s in signals):
            found.append(tech)
    return found


def analyze_page(url):
    """Анализ одной страницы"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SalesBot/1.0)"
        }
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        return resp.text, resp.status_code, resp.url
    except Exception as e:
        return None, str(e), url


def extract_team_info(soup):
    """Извлечение информации о команде"""
    team_keywords = ['team', 'leadership', 'about', 'founders', 'people', 'our people']
    team_data = {
        "has_team_page": False,
        "team_links": [],
    }

    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        text = link.get_text(strip=True).lower()
        if any(kw in href or kw in text for kw in team_keywords):
            team_data["has_team_page"] = True
            team_data["team_links"].append({
                "text": link.get_text(strip=True)[:50],
                "href": link.get('href')
            })

    team_data["team_links"] = team_data["team_links"][:5]
    return team_data


def run_analysis(url):
    """Основной анализ"""
    # Нормализация URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    result = {
        "url": url,
        "analyzed_at": datetime.now().isoformat(),
        "pages_analyzed": 0,
        "company_name": None,
        "company_type": None,
        "description": None,
        "emails": [],
        "phones": [],
        "social_links": {},
        "tech_stack": [],
        "team_info": {},
        "pricing_found": False,
        "blog_found": False,
        "careers_found": False,
        "errors": [],
    }

    if not HAS_BS4:
        result["errors"].append("beautifulsoup4 не установлен. Установи: pip install beautifulsoup4")
        return result

    # Анализ главной страницы
    html, status, final_url = analyze_page(url)

    if html is None:
        result["errors"].append(f"Не удалось загрузить {url}: {status}")
        return result

    soup = BeautifulSoup(html, 'html.parser')
    result["pages_analyzed"] += 1
    result["final_url"] = final_url

    # Название компании
    title_tag = soup.find('title')
    if title_tag:
        result["company_name"] = title_tag.get_text(strip=True).split('|')[0].split('—')[0].split('-')[0].strip()

    # Метаописание
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        result["description"] = meta_desc.get('content', '')[:500]

    # Хабаров страницы
    body_text = soup.get_text(separator=' ', strip=True)[:10000]

    # Тип компании
    result["company_type"] = detect_company_type(body_text + ' ' + (result["description"] or ''))

    # Контакты
    result["emails"] = extract_emails(html)
    result["phones"] = extract_phones(body_text)

    # Соцсети
    result["social_links"] = extract_social_links(html)

    # Стек технологий
    result["tech_stack"] = detect_tech_stack(html)

    # Команда
    result["team_info"] = extract_team_info(soup)

    # Наличие ключевых страниц
    all_links = [a.get('href', '').lower() for a in soup.find_all('a', href=True)]
    all_links_str = ' '.join(all_links)

    result["pricing_found"] = any(kw in all_links_str for kw in ['pricing', 'plans', 'tariffs', 'cost'])
    result["blog_found"] = any(kw in all_links_str for kw in ['blog', 'news', 'insights', 'articles', 'resources'])
    result["careers_found"] = any(kw in all_links_str for kw in ['careers', 'jobs', 'hiring', 'join-us', 'vacancies'])

    # Дополнительные страницы
    subpages_to_check = []
    for kw in ['about', 'team', 'pricing', 'contact', 'careers', 'blog']:
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if kw in href.lower() and href.startswith(('http', '/')):
                if href.startswith('/'):
                    parsed = urlparse(final_url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                if href not in [u for _, u in subpages_to_check]:
                    subpages_to_check.append((kw, href))
                    break

    for page_type, sub_url in subpages_to_check[:4]:
        sub_html, sub_status, _ = analyze_page(sub_url)
        if sub_html:
            result["pages_analyzed"] += 1
            sub_soup = BeautifulSoup(sub_html, 'html.parser')
            sub_text = sub_soup.get_text(separator=' ', strip=True)[:5000]

            # Доп. данные с подстраниц
            sub_emails = extract_emails(sub_html)
            result["emails"] = list(set(result["emails"] + sub_emails))[:5]

            if page_type == 'team':
                result["team_info"]["page_content_preview"] = sub_text[:500]

    # Удаление дублей
    result["emails"] = list(set(result["emails"]))
    result["phones"] = list(set(result["phones"]))

    return result


def main():
    parser = argparse.ArgumentParser(description='Анализ лида — извлечение данных с сайта')
    parser.add_argument('--url', required=True, help='URL сайта компании')
    parser.add_argument('--output', default='json', choices=['json', 'text'], help='Формат вывода')
    parser.add_argument('--file', help='Сохранить результат в файл')
    args = parser.parse_args()

    result = run_analysis(args.url)

    if args.output == 'json':
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = format_text(result)

    print(output)

    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nРезультат сохранён в {args.file}", file=sys.stderr)


def format_text(result):
    """Форматированный текстовый вывод"""
    lines = [
        f"=== Анализ лида ===",
        f"URL: {result['url']}",
        f"Компания: {result.get('company_name', 'N/A')}",
        f"Тип: {result.get('company_type', 'N/A')}",
        f"Страниц проанализировано: {result['pages_analyzed']}",
        "",
        f"Описание: {(result.get('description') or 'N/A')[:200]}",
        "",
        "Контакты:",
        f"  Emails: {', '.join(result['emails']) or 'N/A'}",
        f"  Телефоны: {', '.join(result['phones']) or 'N/A'}",
        "",
        "Соцсети:",
    ]
    for platform, links in result.get('social_links', {}).items():
        lines.append(f"  {platform}: {', '.join(links)}")

    lines.extend([
        "",
        f"Стек: {', '.join(result.get('tech_stack', [])) or 'N/A'}",
        f"Команда: {'да' if result.get('team_info', {}).get('has_team_page') else 'нет'}",
        f"Pricing: {'да' if result.get('pricing_found') else 'нет'}",
        f"Blog: {'да' if result.get('blog_found') else 'нет'}",
        f"Careers: {'да' if result.get('careers_found') else 'нет'}",
    ])

    if result.get('errors'):
        lines.extend(["", "Ошибки:"] + [f"  - {e}" for e in result['errors']])

    return '\n'.join(lines)


if __name__ == '__main__':
    main()