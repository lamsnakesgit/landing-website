import requests
import json

with open("sud_cookies.json", "r") as f:
    cookies = json.load(f)

s = requests.Session()
for c in cookies:
    s.cookies.set(c['name'], c['value'], domain=c['domain'])

r = s.get("https://office.sud.kz/")
if "Войти" in r.text or "Кіру" in r.text:
    print("❌ Сессия НЕ авторизована (Гость)")
else:
    print("✅ Сессия авторизована!")
