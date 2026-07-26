import re
import requests

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

with open("smm_brand_ai/ai_content/love_stories/storyboard/veo31_vertex_generation_pack.md", "r", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(r'## VEO-(\d{2}).*?```text\n(.*?)\n```', re.DOTALL)
matches = pattern.findall(text)

msgs = []
curr_msg = "🎬 *Промпты для Veo 3.1:*\n\n"
for num, prompt in matches:
    # Telegram parse_mode Markdown requires careful escaping, so we won't use it or we'll just use HTML
    chunk = f"<b>VEO-{num}:</b>\n{prompt.strip()}\n\n"
    if len(curr_msg) + len(chunk) > 4000:
        msgs.append(curr_msg)
        curr_msg = chunk
    else:
        curr_msg += chunk
msgs.append(curr_msg)

for m in msgs:
    res = requests.post(API_URL, json={'chat_id': CHAT_ID, 'text': m, 'parse_mode': 'HTML'})
    print(res.json())
