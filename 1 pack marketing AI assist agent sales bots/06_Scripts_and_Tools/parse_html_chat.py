import re
from bs4 import BeautifulSoup
import json
import sys

try:
    with open('chat2.html', 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
except Exception as e:
    print("Error reading file:", e)
    sys.exit(1)

soup = BeautifulSoup(html_content, 'html.parser')

messages = []

for msg_div in soup.find_all('div', class_=re.compile('.*message-in.*|.*message-out.*')):
    text_span = msg_div.find('span', class_=re.compile('.*selectable-text.*'))
    if text_span:
        text = text_span.get_text(separator=' ', strip=True)
        sender_span = msg_div.find('span', attrs={'title': True})
        sender = sender_span.get_text(strip=True) if sender_span else "Unknown"
        phone = sender_span['title'] if sender_span and 'title' in sender_span.attrs else ""
        
        # Simple qualification scoring rule
        # Check if text contains "визитка", "занимаюсь", "услуги", "предлагаю", etc.
        text_lower = text.lower()
        score = 0
        if len(text) > 100: score += 1
        if any(w in text_lower for w in ["помогаю", "занимаюсь", "услуги", "опыт", "эксперт"]): score += 2
        if any(w in text_lower for w in ["разработка", "маркетинг", "ai", "ии", "создание", "продажи"]): score += 2
        if any(w in text_lower for w in ["ищу", "требуется"]): score += 1
        if any(w in text_lower for w in ["визитка"]): score += 1
        
        messages.append({
            "sender": sender,
            "phone": phone,
            "score": score,
            "text": text
        })

messages.sort(key=lambda x: x['score'], reverse=True)

# Save the top leads
with open("leads.json", "w", encoding="utf-8") as out:
    json.dump([m for m in messages if m['score'] > 0], out, ensure_ascii=False, indent=2)

print(f"Extracted {len(messages)} messages. Found {sum(1 for m in messages if m['score'] > 0)} potential leads.")
