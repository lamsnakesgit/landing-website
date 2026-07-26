import re
import requests

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

with open("smm_brand_ai/ai_content/love_stories/storyboard/veo31_vertex_generation_pack.md", "r", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(r'## VEO-(\d{2}).*?```text\n(.*?)\n```', re.DOTALL)
matches = pattern.findall(text)

global_prefix = "Vertical 9:16 realistic cinematic romantic short film in a cozy modern coffee shop in Almaty. Use the provided character reference images and preserve the same heroes, outfits, hair, body proportions, cafe location and warm cinematic style. The woman is the same young Kazakh woman in a beige knit sweater drawing in a sketchbook. The man is the same young Kazakh man in a black hoodie near the coffee bar. Smooth stabilized camera, natural emotional acting, warm cafe lighting, shallow depth of field, soft bokeh. No text overlays, no readable text, no subtitles, no logos, no watermark. "
global_negative = "different face, changed identity, changed outfit, changed hairstyle, distorted face, bad eyes, deformed hands, extra fingers, extra limbs, blurry face, face drift, inconsistent character, text, subtitles, logo, watermark, random letters, overexposed, oversaturated, low resolution, glitch, duplicate person, uncanny expression, shaky camera, extreme motion blur."

msgs = []
curr_msg = "✂️ <b>ПОЛНЫЕ ПРОМПТЫ ДЛЯ КОПИПАСТА (Часть 1)</b>\n\n"
part = 1
for num, prompt in matches:
    full_prompt = global_prefix + prompt.strip()
    chunk = f"<b>VEO-{num}:</b>\n<code>{full_prompt}</code>\n\n"
    if len(curr_msg) + len(chunk) > 4000:
        msgs.append(curr_msg)
        part += 1
        curr_msg = f"✂️ <b>ПОЛНЫЕ ПРОМПТЫ ДЛЯ КОПИПАСТА (Часть {part})</b>\n\n"
        curr_msg += chunk
    else:
        curr_msg += chunk
msgs.append(curr_msg)

# Send negative prompt separately
neg_msg = f"⛔️ <b>GLOBAL NEGATIVE PROMPT</b>\nВставьте этот текст в поле Negative Prompt при ручной генерации:\n\n<code>{global_negative}</code>"
msgs.append(neg_msg)

for m in msgs:
    res = requests.post(API_URL, json={'chat_id': CHAT_ID, 'text': m, 'parse_mode': 'HTML'})
    print(res.json())
